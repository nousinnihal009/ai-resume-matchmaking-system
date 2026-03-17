import sys
import os
import platform

with open("debug_results.txt", "w") as f:
    f.write(f"Python Version: {sys.version}\n")
    f.write(f"OS: {platform.system()} {platform.release()}\n")
    f.write(f"CWD: {os.getcwd()}\n")
    try:
        import fastapi
        f.write(f"FastAPI: {fastapi.__version__}\n")
    except ImportError:
        f.write("FastAPI: NOT FOUND\n")
    
    try:
        import uvicorn
        f.write(f"Uvicorn: {uvicorn.__version__}\n")
    except ImportError:
        f.write("Uvicorn: NOT FOUND\n")

print("DEBUG SCRIPT FINISHED")
