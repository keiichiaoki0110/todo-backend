# auth.pyを元のシンプルなコードに戻す
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError
from .auth_utils import decode_access_token, verify_password, create_access_token, get_password_hash
from ..database import get_db
from sqlalchemy.orm import Session
from ..models import User

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    print(f"📝 ユーザー登録試行: {request.username}")
    
    # ユーザー名の重複チェック
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        print(f"❌ ユーザー名が既に存在: {request.username}")
        raise HTTPException(status_code=400, detail="ユーザー名が既に使用されています")
    
    # メールアドレスの重複チェック
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        print(f"❌ メールアドレスが既に存在: {request.email}")
        raise HTTPException(status_code=400, detail="メールアドレスが既に使用されています")
    
    # 新しいユーザーを作成
    hashed_password = get_password_hash(request.password)
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print(f"✅ ユーザー登録成功: {new_user.username}")
    return {"message": "ユーザー登録が完了しました", "username": new_user.username}

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    print(f"🔐 ログイン試行: {request.username}")
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        print(f"❌ ログイン失敗: {request.username}")
        raise HTTPException(status_code=400, detail="ユーザー名またはパスワードが正しくありません")

    access_token = create_access_token(data={"sub": user.username})
    print(f"✅ ログイン成功: {user.username}, トークン生成完了")
    return {"access_token": access_token, "token_type": "bearer"}

# 🔐 JSON方式とヘッダー方式の両方でトークンを取得する関数
def get_token_from_request(request, authorization: str = None):
    """リクエストからトークンを取得（JSON優先、ヘッダー併用）"""
    token = None
    
    # 1. JSONボディからトークンを取得
    if hasattr(request, 'json') and request.json:
        token = request.json.get('token')
        if token:
            print(f"🔍 JSONボディからトークンを取得: {token[:20]}...")
            return token
    
    # 2. Authorizationヘッダーからトークンを取得
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]  # "Bearer " を除去
        print(f"🔍 Authorizationヘッダーからトークンを取得: {token[:20]}...")
        return token
    
    print("❌ トークンが見つかりません")
    return None

# 🔐 認証されたユーザー情報を取得する関数（他ルートで利用可能）
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    print(f"🔍 認証チェック開始")
    print(f"🔍 受信したトークン: {token[:20] + '...' if token and len(token) > 20 else token or '❌ トークンが空です'}")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が正しくありません",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        print("🔍 トークンをデコード中...")
        payload = decode_access_token(token)
        print(f"✅ デコード成功: {payload}")
        
        username: str = payload.get("sub")
        if username is None:
            print("❌ payloadにsubが含まれていません")
            raise credentials_exception
        print(f"🔍 ユーザー名: {username}")
        
    except JWTError as e:
        print(f"❌ JWT解析エラー: {str(e)}")
        raise credentials_exception
    except Exception as e:
        print(f"❌ 予期しないエラー: {str(e)}")
        raise credentials_exception

    print(f"🔍 データベースでユーザー検索: {username}")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        print(f"❌ ユーザーが見つかりません: {username}")
        raise credentials_exception
    
    print(f"✅ 認証成功: {user.username} (ID: {user.id})")
    return user