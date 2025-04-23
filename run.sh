#!/bin/bash

echo "Starting QualityYouTubeBot..."
echo "==========================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment and run the bot
source venv/bin/activate
python3 QualityYouTubeBot.py 