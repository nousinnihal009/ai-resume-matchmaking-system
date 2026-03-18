"""
Minimal test to check if the app can be imported without errors.
Run from the backend directory:
  python test_import.py
"""
import sys
import traceback

print(f"Python: {sys.version}")
print(f"CWD: {__import__('os').getcwd()}")
print()

try:
    print("Step 1: Importing app.core.config...")
    from app.core.config import settings
    print(f"  OK — database_url={settings.database_url[:30]}...")
except Exception as e:
    print(f"  FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("Step 2: Importing app.db...")
    from app.db import engine, Base
    print(f"  OK — engine={engine}")
except Exception as e:
    print(f"  FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("Step 3: Importing app.core.limiter...")
    from app.core.limiter import limiter
    print(f"  OK — limiter={limiter}")
except Exception as e:
    print(f"  FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("Step 4: Importing app.api modules...")
    from app.api import auth, resumes, jobs, matches, analytics
    print("  OK")
except Exception as e:
    print(f"  FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("Step 5: Importing app.main (full app)...")
    from app.main import app
    print(f"  OK — app={app.title}")
except Exception as e:
    print(f"  FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

print()
print("ALL IMPORTS PASSED — app should start successfully.")
print("Run: uvicorn app.main:app --reload")
