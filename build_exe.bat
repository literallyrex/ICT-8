@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found at .venv\Scripts\python.exe
    exit /b 1
)

call ".venv\Scripts\activate.bat"

for /f "delims=" %%i in ('python -c "import sys; print(sys.base_prefix)"') do set "PY_BASE=%%i"
set "TCL_DIR=%PY_BASE%\tcl\tcl8.6"
set "TK_DIR=%PY_BASE%\tcl\tk8.6"

if not exist "%TCL_DIR%\init.tcl" (
    echo Tcl data folder not found at "%TCL_DIR%"
    exit /b 1
)

if not exist "%TK_DIR%\tk.tcl" (
    echo Tk data folder not found at "%TK_DIR%"
    exit /b 1
)

set "TCL_LIBRARY=%TCL_DIR%"
set "TK_LIBRARY=%TK_DIR%"

python -m PyInstaller --clean --noconfirm --specpath "build" --onefile --windowed --name "StudentRegistrationSystem" ^
  --add-data "logo.png;." ^
  --add-data "%TCL_DIR%;_tcl_data" ^
  --add-data "%TK_DIR%;_tk_data" ^
  --hidden-import=tkinter ^
  --hidden-import=tkinter.ttk ^
  --hidden-import=tkinter.filedialog ^
  --hidden-import=tkinter.messagebox ^
  --hidden-import=tkinter.font ^
  --hidden-import=tkinter.simpledialog ^
  --hidden-import=tkinter.constants ^
  --hidden-import=_tkinter ^
  --collect-all customtkinter ^
  --collect-all tkintermapview ^
  --collect-all matplotlib ^
  --collect-all mysql ^
  --collect-all geopy ^
  main.py

if errorlevel 1 (
    echo.
    echo Build failed.
    exit /b 1
)

echo.
echo Build finished.
echo EXE: dist\StudentRegistrationSystem.exe
endlocal
