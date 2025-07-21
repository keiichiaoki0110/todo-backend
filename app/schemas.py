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
