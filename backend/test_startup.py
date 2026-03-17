"""Quick test to check if the backend app can be imported."""
import sys
import traceback

print("Python version:", sys.version)
print("Testing imports step by step...")
print()

# Step 1: Test schema base
try:
    print("[1] Importing schemas.base...")
    from app.schemas.base import APIResponse
    print("    OK: APIResponse imported")
    # Test parameterization
    test = APIResponse[dict]
    print("    OK: APIResponse[dict] works")
except Exception as e:
    print(f"    FAIL: {e}")
    traceback.print_exc()

# Step 2: Test db models
try:
    print("[2] Importing db.models...")
    from app.db.models import Base, Resume, Job, User
    print("    OK: All models imported")
except Exception as e:
    print(f"    FAIL: {e}")
    traceback.print_exc()

# Step 3: Test db session
try:
    print("[3] Importing db.session...")
    from app.db.session import engine, get_db
    print("    OK: engine and get_db imported")
except Exception as e:
    print(f"    FAIL: {e}")
    traceback.print_exc()

# Step 4: Test core config
try:
    print("[4] Importing core.config...")
    from app.core.config import settings
    print(f"    OK: settings.app_name = {settings.app_name}")
except Exception as e:
    print(f"    FAIL: {e}")
    traceback.print_exc()

# Step 5: Test API modules
for mod_name in ["auth", "resumes", "jobs", "matches", "analytics"]:
    try:
        print(f"[5.{mod_name}] Importing api.{mod_name}...")
        __import__(f"app.api.{mod_name}")
        print(f"    OK: api.{mod_name} imported")
    except Exception as e:
        print(f"    FAIL: {e}")
        traceback.print_exc()

# Step 6: Test full app
try:
    print("[6] Importing app.main (full app)...")
    from app.main import app
    print("    OK: FastAPI app created successfully!")
except Exception as e:
    print(f"    FAIL: {e}")
    traceback.print_exc()

print()
print("=== Test complete ===")
