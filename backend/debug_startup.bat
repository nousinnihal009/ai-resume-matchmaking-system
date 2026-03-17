@echo off
set VIRTUAL_ENV=c:\CODES\project_nousin\ai-resume-matchmaking-system\.venv
set PATH=%VIRTUAL_ENV%\Scripts;%PATH%
python --version > py_out.txt 2>&1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > uvicorn_out.txt 2>&1
echo DONE
