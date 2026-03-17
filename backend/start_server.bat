@echo off
set "PYTHON_EXE=c:\CODES\project_nousin\ai-resume-matchmaking-system\.venv\Scripts\python.exe"
%PYTHON_EXE% -m uvicorn app.main:app --host 127.0.0.1 --port 8000
