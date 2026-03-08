@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found at .venv\Scripts\python.exe
    exit /b 1
)

call ".venv\Scripts\activate.bat"
python -m PyInstaller --clean --noconfirm "StudentRegistrationSystem.spec"

if errorlevel 1 (
    echo.
    echo Build failed.
    exit /b 1
)

echo.
echo Build finished.
echo EXE: dist\StudentRegistrationSystem.exe
endlocal
