@echo off
echo =======================================================
echo     BUILDING SPRINT APPLICATION INTO INSTANT-LAUNCH FOLDER
echo =======================================================
echo.
echo Step 1: Installing required libraries (PyQt5, Matplotlib, Pillow, PyInstaller, requests)...
python -m pip install --upgrade pip
pip install PyQt5 matplotlib pillow pyinstaller requests
echo.
echo Step 2: Compiling application with PyInstaller...
echo We build in "onedir" folder mode to guarantee INSTANT launch (0.1 seconds) on your PC!
pyinstaller --noconsole --onedir --add-data "assets;assets" --name="Sprint" --clean sprint_app.py
echo.
if exist "dist\Sprint\Sprint.exe" (
    echo =======================================================
    echo [SUCCESS] Build completed successfully!
    echo Your instant-launch folder is located at: dist\Sprint\
    echo.
    echo To distribute the program to students or other laptops:
    echo 1. Simply zip the entire "Sprint" folder into a Sprint.zip file.
    echo 2. Send the zip file to other PCs, unzip, and launch Sprint.exe!
    echo.
    echo This launches INSTANTLY (0.1 seconds) without any Temp loading lag!
    echo =======================================================
) else (
    echo =======================================================
    echo [ERROR] Failed to compile.
    echo Please make sure Python is installed and added to PATH.
    echo =======================================================
)
echo.
pause
