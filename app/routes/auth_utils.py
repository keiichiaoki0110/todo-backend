from jose import JWTError, jwt  # JWTトークンの生成と検証
from passlib.context import CryptContext  # パスワードのハッシュ化
from datetime import datetime, timedelta

# 秘密鍵とアルゴリズムの設定
SECRET_KEY = "your_secret_key"  # 実際のプロジェクトでは環境変数で管理
ALGORITHM = "HS256"  # ハッシュアルゴリズム

# パスワードのハッシュ化コンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 平文のパスワードとハッシュ化されたパスワードを比較
def verify_password(plain_password, hashed_password):
    """
    平文のパスワードがハッシュと一致するかを検証
    """
    return pwd_context.verify(plain_password, hashed_password)

# パスワードをハッシュ化
def get_password_hash(password):
    """
    平文のパスワードをハッシュ化
    """
    return pwd_context.hash(password)

# アクセストークンの生成
def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    JWTトークンを生成
    """
    to_encode = data.copy()  # データをコピー
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))  # 有効期限を設定
    to_encode.update({"exp": expire})  # トークンに有効期限を追加
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# アクセストークンのデコード
def decode_access_token(token: str):
    """
    JWTトークンをデコードし、中身を返す
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
