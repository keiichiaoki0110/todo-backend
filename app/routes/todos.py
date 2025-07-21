from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Todo, User
from app.schemas import TodoCreate, TodoResponse
from app.database import get_db
from .auth import get_current_user
from typing import List

# ルーターの作成（エンドポイントのプレフィックスとタグを設定）
router = APIRouter(prefix="/todos", tags=["todos"])

# タスク一覧を取得するエンドポイント
@router.get("", response_model=List[TodoResponse])
def get_todos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    現在のユーザーに紐づくタスクを全て取得
    """
    return db.query(Todo).filter(Todo.user_id == current_user.id).all()

# タスクを作成するエンドポイント
@router.post("", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    新しいタスクを作成
    """
    # Todoモデルにスキーマのデータを詰めて新規作成
    new_todo = Todo(**todo.dict(), user_id=current_user.id)
    db.add(new_todo)  # データベースに追加
    db.commit()  # 変更を保存
    db.refresh(new_todo)  # 新しいデータをリロード
    return new_todo

# タスクを更新するエンドポイント
@router.put("/{task_id}", response_model=TodoResponse)
def update_todo(task_id: int, todo: TodoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    指定したIDのタスクを更新
    """
    # 指定IDのタスクを取得
    existing_todo = db.query(Todo).filter(Todo.id == task_id, Todo.user_id == current_user.id).first()
    if not existing_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    # 更新するフィールドを設定
    for key, value in todo.dict(exclude_unset=True).items():
        setattr(existing_todo, key, value)
    db.commit()  # 保存
    db.refresh(existing_todo)  # データをリロード
    return existing_todo

# タスクを削除するエンドポイント
@router.delete("/{task_id}")
def delete_todo(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    指定したIDのタスクを削除
    """
    todo = db.query(Todo).filter(Todo.id == task_id, Todo.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)  # データを削除
    db.commit()  # 保存
    return {"message": "タスクが削除されました"}

# タスクの完了/未完了を切り替えるエンドポイント
@router.put("/{task_id}/toggle", response_model=TodoResponse)
def toggle_task_complete(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    指定したIDのタスクの完了状態を切り替え
    """
    task = db.query(Todo).filter(Todo.id == task_id, Todo.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Todo not found")
    task.completed = not task.completed  # 完了フラグを反転
    db.commit()  # 保存
    db.refresh(task)  # データをリロード
    return task
