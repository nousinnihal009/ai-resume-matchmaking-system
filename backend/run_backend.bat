@echo off
cd c:\CODES\project_nousin\ai-resume-matchmaking-system\backend
call ..\.venv\Scripts\activate.bat
uvicorn app.main:app --reload
