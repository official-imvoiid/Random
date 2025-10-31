@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo    Hugging Face Cache Location Setter
echo ==========================================
echo.
echo This will help you set a custom location for Hugging Face cache.
echo.

REM Create temporary VBScript for folder selection
set "tempvbs=%temp%\selectfolder.vbs"

(
echo Set objShell = CreateObject("Shell.Application"^)
echo Set objFolder = objShell.BrowseForFolder(0, "Select ANY folder for Hugging Face cache (C:, D:, USB, Network...^):", 17, 0^)
echo If Not objFolder Is Nothing Then
echo     WScript.Echo objFolder.Self.Path
echo Else
echo     WScript.Echo "CANCELLED"
echo End If
) > "%tempvbs%"

REM Show folder picker dialog and get result
echo Please select your desired Hugging Face cache folder...
echo (You can choose ANY location: C:, D:, USB drives, external drives, network locations, etc.)
echo.
for /f "delims=" %%i in ('cscript //nologo "%tempvbs%"') do set "selectedfolder=%%i"

REM Clean up temporary file
del "%tempvbs%" 2>nul

REM Check if user cancelled
if "!selectedfolder!"=="CANCELLED" (
    echo.
    echo [CANCELLED] No folder selected. Exiting...
    pause
    exit /b 0
)

REM Show selected folder
echo.
echo Selected folder: !selectedfolder!
echo.

REM Confirm selection
echo The following environment variables will be set:
echo   HF_HOME = !selectedfolder!
echo   HUGGINGFACE_HUB_CACHE = !selectedfolder!\hub
echo.
set /p "confirm=Do you want to proceed? (Y/N): "

if /i not "!confirm!"=="Y" (
    echo.
    echo [CANCELLED] Operation cancelled by user.
    pause
    exit /b 0
)

echo.
echo Setting environment variables...

REM Set environment variables permanently
setx HF_HOME "!selectedfolder!" >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Failed to set HF_HOME
    pause
    exit /b 1
)

setx HUGGINGFACE_HUB_CACHE "!selectedfolder!\hub" >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Failed to set HUGGINGFACE_HUB_CACHE
    pause
    exit /b 1
)

echo [SUCCESS] Environment variables set successfully!

REM Create directories if they don't exist
echo.
echo Creating directories...

if not exist "!selectedfolder!" (
    mkdir "!selectedfolder!" 2>nul
    if exist "!selectedfolder!" (
        echo [SUCCESS] Created: !selectedfolder!
    ) else (
        echo [ERROR] Failed to create: !selectedfolder!
        echo Please check folder permissions.
    )
) else (
    echo [EXISTS] Directory already exists: !selectedfolder!
)

if not exist "!selectedfolder!\hub" (
    mkdir "!selectedfolder!\hub" 2>nul
    if exist "!selectedfolder!\hub" (
        echo [SUCCESS] Created: !selectedfolder!\hub
    ) else (
        echo [ERROR] Failed to create: !selectedfolder!\hub
        echo Please check folder permissions.
    )
) else (
    echo [EXISTS] Hub directory already exists: !selectedfolder!\hub
)

REM Set variables for current session
set "HF_HOME=!selectedfolder!"
set "HUGGINGFACE_HUB_CACHE=!selectedfolder!\hub"

echo.
echo ==========================================
echo              SETUP COMPLETE!
echo ==========================================
echo.
echo Your Hugging Face cache is now set to:
echo   HF_HOME: !selectedfolder!
echo   HUGGINGFACE_HUB_CACHE: !selectedfolder!\hub
echo.
echo IMPORTANT: Restart any applications using Hugging Face
echo (Python IDE, Command Prompt, Jupyter, etc.) for changes to take effect.
echo.

REM Ask if user wants to test the setting
set /p "test=Do you want to test the setting now? (Y/N): "
if /i "!test!"=="Y" (
    echo.
    echo Testing environment variables...
    echo HF_HOME = %HF_HOME%
    echo HUGGINGFACE_HUB_CACHE = %HUGGINGFACE_HUB_CACHE%
    echo.
    echo Note: These show current session values.
    echo New applications will use the permanent settings.
)

echo.
echo Press any key to exit...
pause >nul