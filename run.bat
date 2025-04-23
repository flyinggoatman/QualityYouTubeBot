@echo off
echo Starting QualityYouTubeBot...
echo ===========================

REM Check if virtual environment exists
if not exist venv (
    echo Error: Virtual environment not found. Please run setup.bat first.
    goto end
)

REM Activate virtual environment and run the bot
call venv\Scripts\activate
python QualityYouTubeBot.py

:end
pause 