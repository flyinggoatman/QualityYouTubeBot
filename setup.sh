#!/bin/bash

echo "QualityYouTubeBot Setup Script"
echo "==========================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2)
if [[ ! $python_version =~ ^3\.([8-9]|1[0-9])\. ]]; then
    echo "Error: Please ensure you have Python 3.8 or higher installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment and install dependencies
echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp ".env template" .env
    echo "Please edit the .env file with your configuration before running the bot."
else
    echo ".env file already exists."
fi

echo
echo "Setup completed!"
echo
echo "To run the bot:"
echo "1. Make sure your .env file is configured correctly"
echo "2. Run './run.sh' or 'python3 QualityYouTubeBot.py'"
echo "2.1.if you want the bot to run on boot then put  run.bat in startup folder on windows."
echo

# Make run.sh executable
if [ -f "run.sh" ]; then
    chmod +x run.sh
fi

chmod +x setup.sh 