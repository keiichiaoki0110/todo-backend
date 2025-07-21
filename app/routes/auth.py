from fastapi import FastAPI
from fastapi import APIRouter
from app.models import User

# APIRouterを作成
router = APIRouter(
    prefix="/auth",  # 全エンドポイントに適用されるURLのプレフィックス
    tags=["auth"],   # Swagger UIでのタグ名
)

# 仮のエンドポイント
@router.get("/mock-user")
def get_current_user():
    # 仮のユーザーオブジェクトを返す
    return User(id=1, username="mock_user", email="mock@example.com")


from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.schemas import UserCreate, UserLogin
from app.models import User
from app.database import get_db
from .auth_utils import verify_password, get_password_hash, create_access_token
from datetime import timedelta

# 認証ルーターを作成
router = APIRouter(prefix="/auth", tags=["auth"])

# トークンを取得するためのエンドポイントのURL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ユーザー登録エンドポイント
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    新しいユーザーを登録する
    """
    # ユーザー名またはメールアドレスが既に存在するか確認
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    # パスワードをハッシュ化して新しいユーザーを作成
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "アカウントが作成されました"}

# ログインエンドポイント
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    ログインしてアクセストークンを取得する
    """
    # ユーザーをデータベースから取得
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # JWTトークンを生成して返す
    access_token = create_access_token(data={"sub": str(db_user.id)}, expires_delta=timedelta(minutes=30))
    return {"token": access_token}

# 現在のユーザーを取得するヘルパー関数
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    トークンからユーザー情報を取得する
    """
    from .auth_utils import decode_access_token
    payload = decode_access_token(token)  # トークンをデコード
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
