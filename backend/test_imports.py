try:
    print("Importing settings...")
    from app.core.config import settings
    print("Importing models...")
    from app.db import engine, Base
    print("Importing routers...")
    from app.api import auth, resumes, jobs, matches, analytics
    print("Importing limiter...")
    from app.core.limiter import limiter
    print("ALL IMPORTS SUCCESSFUL")
except Exception as e:
    print(f"IMPORT FAILED: {e}")
    import traceback
    traceback.print_exc()
