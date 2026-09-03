@echo off
REM Run the stub Order Service (Part D). Leave this window open.
cd /d "%~dp0"
call ".venv\Scripts\activate.bat"
cd "Part D - Survive the Network"
python stub_order_service.py
pause
