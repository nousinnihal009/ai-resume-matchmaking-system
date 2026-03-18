from app.core.security import create_access_token
import traceback

print("Testing create_access_token...")
try:
    token = create_access_token({"sub": "test-id", "role": "student"})
    print(f"Token generated successfully: {token[:20]}...")
except Exception as e:
    print("FAILED TO GENERATE TOKEN:")
    traceback.print_exc()
