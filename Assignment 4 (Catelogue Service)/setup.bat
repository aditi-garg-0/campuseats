@echo off
REM One-time setup. Double-click this first.
cd /d "%~dp0"

echo Creating virtual environment in .venv ...
python -m venv .venv

echo Installing dependencies ...
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ============================================
echo Setup complete.
echo Next: run "run_order_service.bat" and
echo "run_catalogue_service.bat" (in two separate
echo windows), then "run_tests.bat" whenever you like.
echo ============================================
pause
