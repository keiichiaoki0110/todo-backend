from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, todos
from .database import Base, engine

# データベースの初期化
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS の設定
origins = [
    "http://localhost",  # フロントエンドが動作しているドメイン
    "http://127.0.0.1:3000",  # 必要に応じて他のオリジンも追加
]

# CORS ミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 必要に応じて特定のオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],  # すべての HTTP メソッドを許可
    allow_headers=["*"],  # すべてのヘッダーを許可
)

# ルーターを追加
app.include_router(auth.router)
app.include_router(todos.router)

