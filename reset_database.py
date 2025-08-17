#!/usr/bin/env python3
"""
データベースリセットスクリプト
既存のデータベースファイルを削除して、新しいテーブル構造で再作成します。
"""

import os
import sys
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import Base, engine
from app.models import User, Todo

def reset_database():
    """データベースを完全にリセットする"""
    
    # データベースファイルのパス
    db_files = [
        "todo_app.db",
        "test.db",
        "app/routes/todo_app.db"  # routes フォルダ内にもある場合
    ]
    
    print("🗑️  既存のデータベースファイルを削除中...")
    
    # 既存のデータベースファイルを削除
    for db_file in db_files:
        db_path = project_root / db_file
        if db_path.exists():
            try:
                os.remove(db_path)
                print(f"   ✅ 削除完了: {db_file}")
            except Exception as e:
                print(f"   ❌ 削除失敗: {db_file} - {e}")
        else:
            print(f"   ℹ️  ファイルが存在しません: {db_file}")
    
    print("\n🔨 新しいデータベーステーブルを作成中...")
    
    try:
        # 新しいテーブル構造で作成
        Base.metadata.create_all(bind=engine)
        print("   ✅ テーブル作成完了!")
        
        # 作成されたテーブルの確認
        print("\n📋 作成されたテーブル:")
        for table_name in Base.metadata.tables.keys():
            print(f"   - {table_name}")
            
    except Exception as e:
        print(f"   ❌ テーブル作成失敗: {e}")
        return False
    
    print("\n🎉 データベースリセット完了!")
    print("   新しいテーブル構造:")
    print("   - users: id, username, email, hashed_password")
    print("   - todos: id, title, details, completed, createdAt, updatedAt, user_id")
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("🔄 Todo アプリケーション データベースリセット")
    print("=" * 50)
    
    # 確認メッセージ
    response = input("\n⚠️  既存のデータがすべて削除されます。続行しますか？ (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        success = reset_database()
        if success:
            print("\n✨ リセット完了! サーバーを再起動してください。")
        else:
            print("\n❌ リセット中にエラーが発生しました。")
            sys.exit(1)
    else:
        print("\n🚫 リセットをキャンセルしました。")