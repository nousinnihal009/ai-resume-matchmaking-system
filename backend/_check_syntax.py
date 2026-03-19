"""Quick syntax check for all new/modified files."""
import py_compile
import sys

files = [
    "app/worker/__init__.py",
    "app/worker/celery_app.py",
    "app/worker/tasks.py",
    "app/worker/gdpr_tasks.py",
    "app/schemas/gdpr.py",
    "app/services/gdpr_service.py",
    "app/api/gdpr.py",
    "app/api/matches.py",
    "app/api/resumes.py",
    "app/main.py",
    "app/core/config.py",
]

errors = []
for f in files:
    try:
        py_compile.compile(f, doraise=True)
        print(f"  OK: {f}")
    except py_compile.PyCompileError as e:
        print(f"FAIL: {f} -> {e}")
        errors.append(f)

if errors:
    print(f"\n{len(errors)} file(s) failed syntax check")
    sys.exit(1)
else:
    print(f"\nAll {len(files)} files compile OK")
