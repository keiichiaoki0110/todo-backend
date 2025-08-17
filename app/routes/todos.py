from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from app.models import Todo, User
from app.schemas import TodoCreate, TodoResponse
from app.database import get_db
from .auth import get_current_user, get_token_from_request, decode_access_token
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(tags=["todos"])

# JSON方式のリクエスト用スキーマ
class TodoCreateWithToken(TodoCreate):
    token: Optional[str] = None

class TodoUpdateWithToken(BaseModel):
    title: Optional[str] = None
    details: Optional[str] = None
    token: Optional[str] = None

# JSON方式の認証ユーザー取得（デバッグ強化版）
async def get_current_user_json(
    todo_data: TodoCreateWithToken,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """JSON方式またはヘッダー方式でトークンを取得して認証"""
    print("🔍 JSON方式認証開始")
    print(f"🔍 受信データ: {todo_data}")
    
    # JSONボディからトークンを取得
    token = todo_data.token
    print(f"🔍 JSONからのトークン: {token[:20] + '...' if token else 'None'}")
    
    # ヘッダーからトークンを取得（フォールバック）
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        print(f"🔍 Authorizationヘッダーからトークン取得: {token[:20]}...")
    
    if not token:
        print("❌ トークンが見つかりません")
        raise HTTPException(status_code=401, detail="認証トークンが必要です")
    
    # トークンを検証
    try:
        print(f"🔍 トークン検証開始: {token[:30]}...")
        payload = decode_access_token(token)
        print(f"🔍 デコード結果: {payload}")
        
        username = payload.get("sub")
        if not username:
            print("❌ payloadにsubが含まれていません")
            raise HTTPException(status_code=401, detail="無効なトークンです")
        
        print(f"🔍 ユーザー名: {username}")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"❌ ユーザーが見つかりません: {username}")
            raise HTTPException(status_code=401, detail="ユーザーが見つかりません")
        
        print(f"✅ JSON方式認証成功: {user.username}")
        return user
    except Exception as e:
        print(f"❌ JSON方式認証エラー詳細: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=401, detail=f"認証に失敗しました: {str(e)}")

# タスク一覧を取得
@router.get("", response_model=List[TodoResponse])
def get_todos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Todo).filter(Todo.user_id == current_user.id).all()

# タスクを作成（ヘッダー方式）
@router.post("", response_model=TodoResponse)
def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("✅ POST /todos (ヘッダー方式) にアクセスされました")
    print("受け取ったデータ:", todo)
    print("現在のユーザー:", current_user.username)

    try:
        new_todo = Todo(**todo.dict(), user_id=current_user.id)
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)
        return new_todo
    except Exception as e:
        print("❌ タスク作成中にエラー:", str(e))
        raise HTTPException(status_code=500, detail="タスクの作成に失敗しました")

# タスクを作成（JSON方式）
@router.post("/json", response_model=TodoResponse)
async def create_todo_json(
    todo_data: TodoCreateWithToken,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    print("✅ POST /todos/json (JSON方式) にアクセスされました")
    print("受け取ったデータ:", todo_data)
    
    # JSON方式でユーザー認証
    current_user = await get_current_user_json(todo_data, authorization, db)
    
    try:
        # tokenフィールドを除外してTodoを作成
        todo_dict = todo_data.dict(exclude={'token'})
        new_todo = Todo(**todo_dict, user_id=current_user.id)
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)
        print(f"✅ JSON方式でタスク作成成功: {new_todo.title}")
        return new_todo
    except Exception as e:
        print("❌ JSON方式タスク作成中にエラー:", str(e))
        raise HTTPException(status_code=500, detail="タスクの作成に失敗しました")

# タスクを更新
@router.put("/{task_id}", response_model=TodoResponse)
def update_todo(task_id: int, todo: TodoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing_todo = db.query(Todo).filter(Todo.id == task_id, Todo.user_id == current_user.id).first()
    if not existing_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, value in todo.dict(exclude_unset=True).items():
        setattr(existing_todo, key, value)
    db.commit()
    db.refresh(existing_todo)
    return existing_todo

# タスクを削除
@router.delete("/{task_id}")
def delete_todo(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == task_id, Todo.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "タスクが削除されました"}

# タスクの完了状態を切り替え
@router.put("/{task_id}/toggle", response_model=TodoResponse)
def toggle_task_complete(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Todo).filter(Todo.id == task_id, Todo.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Todo not found")
    task.completed = not task.completed
    db.commit()
    db.refresh(task)
    return task
