@echo on
echo =======================================================
echo          DIAGNOSTIC BUILD FOR SPRINT APPLICATION
echo =======================================================
echo.

echo [STEP 1] Checking Python version:
python --version
if errorlevel 1 (
    echo [ERROR] Python is not installed or not added to PATH!
    echo Please download Python from python.org and check "Add Python to PATH".
    goto end
)
pause

echo.
echo [STEP 2] Checking pip installer:
pip --version
if errorlevel 1 (
    echo [ERROR] pip is not found. Python installation might be corrupted.
    goto end
)
pause

echo.
echo [STEP 3] Upgrading pip:
python -m pip install --upgrade pip
pause

echo.
echo [STEP 4] Installing dependencies:
pip install PyQt5 matplotlib pillow pyinstaller requests
if errorlevel 1 (
    echo [ERROR] Failed to install libraries. Check your internet connection.
    goto end
)
pause

echo.
echo [STEP 5] Compiling with PyInstaller:
pyinstaller --noconsole --onefile --name="Sprint" --clean sprint_app.py
if errorlevel 1 (
    echo [ERROR] PyInstaller compilation failed! Copy the error above.
    goto end
)

echo.
if exist "dist\Sprint.exe" (
    echo =======================================================
    echo [SUCCESS] Sprint.exe was created inside 'dist' folder!
    echo =======================================================
) else (
    echo [ERROR] Process finished but Sprint.exe was not found.
)

:end
pause
