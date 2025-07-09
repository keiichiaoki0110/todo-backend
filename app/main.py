from fastapi import FastAPI
from app.database import engine, Base

app = FastAPI()

# モデルをもとにテーブル作成
Base.metadata.create_all(bind=engine)
