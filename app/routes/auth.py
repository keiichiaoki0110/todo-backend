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
