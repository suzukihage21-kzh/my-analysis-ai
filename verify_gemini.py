import os
import sys

# プロジェクトルートをパスに追加
sys.path.append(os.getcwd())

from dotenv import load_dotenv
from logic.ai_analyzer import get_gemini_client

# 環境変数を読み込み
load_dotenv()

def verify_gemini():
    print("Gemini API connecting test...")
    
    # Check client initialization
    client = get_gemini_client()
    if not client:
        print("[ERROR] Client initialization failed.")
        print("  - Check if .env file exists")
        print("  - Check if GEMINI_API_KEY is correct")
        return

    print("[OK] Client initialized successfully")

    # Simple generation test
    try:
        print("Sending request to API (gemini-flash-latest)...")
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents="Hello. This is a test. Please reply shortly."
        )
        print(f"[OK] API Call Successful!\nResponse: {response.text}")
        print("-" * 50)
        print("[SUCCESS] Gemini API setup and verification complete!")
            
    except Exception as e:
        print(f"[ERROR] Error occurred during API call: {e}")

if __name__ == "__main__":
    verify_gemini()
