@echo off
echo Downloading latest WinPython from SourceForge...
echo.

REM Create Py312 directory if it doesn't exist
if not exist "Py312" mkdir Py312

REM Download latest WinPython using curl
echo Downloading WinPython.exe...
curl -L "https://sourceforge.net/projects/winpython/files/latest/download" -o "WinPython.exe"

REM Check if download was successful
if not exist "WinPython.exe" (
    echo ERROR: Download failed!
    pause
    exit /b 1
)

echo Download completed successfully!
echo.

REM Extract WinPython directly to Py312 folder
echo Extracting WinPython to Py312...
"WinPython.exe" -o"Py312" -y >nul 2>&1

REM Move files from the nested folder to Py312 root
echo Moving files to Py312 root...
for /d %%i in (Py312\WPy64-*) do (
    xcopy "%%i\*" "Py312\" /E /H /Y /Q >nul 2>&1
    rmdir /s /q "%%i" >nul 2>&1
)

echo Extraction completed!
echo.

REM Delete the downloaded exe file
echo Deleting downloaded file...
del "WinPython.exe"

echo.
echo WinPython has been installed to Py312 folder!
echo.
pause