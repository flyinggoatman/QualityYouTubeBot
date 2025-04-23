@echo off
echo QualityYouTubeBot Setup Script
echo ===========================

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python not found. Please install Python 3.8 or higher.
    goto end
)

REM Check Python version
python --version | findstr /R "3\.[89]\|3\.1[0-9]" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Please ensure you have Python 3.8 or higher installed.
    goto end
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment and install dependencies
echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate
pip install -r requirements.txt

REM Check if .env file exists
if not exist .env (
    echo Creating .env file from template...
    copy ".env template" .env
    echo Please edit the .env file with your configuration before running the bot.
) else (
    echo .env file already exists.
)

echo.
echo Setup completed!
echo.
echo To run the bot:
echo 1. Make sure your .env file is configured correctly
echo 2. Run "python QualityYouTubeBot.py"
echo.
echo Or simply run "run.bat" if available.

:end
pause 