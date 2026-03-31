import ast, sys, os

files = [
    r'backend\app\core\model_manager.py',
    r'backend\app\pipeline\embeddings.py',
    r'backend\app\pipeline\matching.py',
    r'backend\app\core\config.py',
    r'backend\app\db\models.py',
    r'backend\app\services\match_service.py',
    r'backend\app\worker\tasks.py',
    r'backend\app\api\jobs.py',
    r'backend\app\main.py',
    r'backend\alembic\versions\0002_add_vector_indexes.py',
]

errors = []
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as fh:
            source = fh.read()
        ast.parse(source, filename=f)
        print(f"  OK: {f}")
    except SyntaxError as e:
        print(f"  FAIL: {f} -> line {e.lineno}: {e.msg}")
        errors.append(f)

if errors:
    print(f"\n{len(errors)} file(s) have syntax errors!")
    sys.exit(1)
else:
    print("\nALL 10 FILES PASS SYNTAX CHECK")
