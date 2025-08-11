# auth.pyを元のシンプルなコードに戻す
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError
from .auth_utils import decode_access_token, verify_password, create_access_token
from ..database import get_db
from sqlalchemy.orm import Session
from ..models import User

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class LoginRequest(BaseModel):
    username: str
    password: str

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