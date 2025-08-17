from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, todos
from .database import Base, engine

# モデルをDBに作成
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS設定（React側との通信を許可）
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 認証ルーター → /auth/login などで使える
app.include_router(auth.router, prefix="/auth")

# todosルーター → `/todos` プレフィックスでルーティング
app.include_router(todos.router, prefix="/todos")
