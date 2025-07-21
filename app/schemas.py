from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 基本のタスクスキーマ
class TodoBase(BaseModel):
    title: str  # タスクのタイトル（必須）
    details: Optional[str] = None  # タスクの詳細（任意）

# タスク作成用のスキーマ
class TodoCreate(TodoBase):
    pass  # TodoBaseと同じ内容なので、そのまま継承

# タスクレスポンス用のスキーマ
class TodoResponse(TodoBase):
    id: int  # タスクID
    createdAt: datetime  # 作成日時
    updatedAt: datetime  # 更新日時
    completed: bool  # 完了フラグ

    class Config:
        # ORM（データベースモデル）からデータを読み取る設定
        from_attributes = True
from pydantic import BaseModel, EmailStr

# ユーザー登録用のスキーマ
class UserCreate(BaseModel):
    username: str  # ユーザー名
    email: EmailStr  # メールアドレス（形式チェック付き）
    password: str  # パスワード

    class Config:
        from_attributes = True

# ユーザーログイン用のスキーマ
class UserLogin(BaseModel):
    username: str  # ユーザー名
    password: str  # パスワード

    class Config:
        from_attributes = True