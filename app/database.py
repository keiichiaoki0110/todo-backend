from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# データベースのURLは環境に合わせて変更してください（例はSQLite）
SQLALCHEMY_DATABASE_URL = "sqlite:///./todo_app.db"

# エンジン作成
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# セッションローカル作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Baseクラスの定義（モデルの基底クラス）
Base = declarative_base()

# DBセッションの依存関係（FastAPIのDependsで使う）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
