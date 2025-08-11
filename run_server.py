# run_server.py - バックエンドサーバー起動スクリプト
import uvicorn
import os

if __name__ == "__main__":
    print("🚀 FastAPI Todo バックエンドサーバーを起動中...")
    print("📍 URL: http://localhost:8000")
    print("📖 API ドキュメント: http://localhost:8000/docs")
    print("🔄 CORS設定: React (localhost:3000) との通信を許可")
    print("=" * 50)
    
    # アプリケーションディレクトリに移動
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )