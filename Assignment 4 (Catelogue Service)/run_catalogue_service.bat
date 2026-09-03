@echo off
REM Run the Catalogue Service (Part C). Leave this window open.
REM Start run_order_service.bat FIRST, in its own window.
cd /d "%~dp0"
call ".venv\Scripts\activate.bat"
set ORDER_SERVICE_URL=http://localhost:5001
cd "Part C - Implement It"
python app.py
pause
