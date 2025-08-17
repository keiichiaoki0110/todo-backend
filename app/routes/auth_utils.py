from jose import JWTError, jwt  # JWTトークンの生成と検証
from passlib.context import CryptContext  # パスワードのハッシュ化
from datetime import datetime, timedelta
from typing import Optional

# セキュリティ設定（本番では環境変数で管理）
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# パスワードハッシュ用コンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# パスワード検証
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# パスワードをハッシュ化
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# アクセストークンの生成
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    ユーザー情報を含むJWTトークンを作成
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    if "sub" not in to_encode:
        raise ValueError("create_access_token に 'sub'（ユーザー識別子）が含まれていません。")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# アクセストークンのデコード
def decode_access_token(token: str) -> dict:
    """
    JWTトークンを検証して中身（ペイロード）を返す
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if "sub" not in payload:
            raise JWTError("sub がトークンに含まれていません。")
        return payload
    except JWTError as e:
        raise JWTError(f"無効なトークン: {str(e)}")
