#!/bin/bash

# MAC Assistant Setup Script for Windows
echo "Setting up MAC Assistant..."

# Check if Python is installed
python --version
if [ $? -ne 0 ]; then
    echo "Python is not installed. Please install Python 3.8 or later."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/Scripts/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
pip install -r requirements-windows.txt

# Create models directory
echo "Creating models directory..."
mkdir -p models

# Download Vosk model (small English model)
echo "Downloading Vosk speech recognition model..."
cd models
if [ ! -d "vosk-model" ]; then
    echo "Please download a Vosk model manually:"
    echo "1. Go to https://alphacephei.com/vosk/models"
    echo "2. Download vosk-model-small-en-us-0.15.zip"
    echo "3. Extract it to models/vosk-model/"
fi
cd ..

echo "Setup complete!"
echo ""
echo "To run MAC Assistant:"
echo "1. Activate the virtual environment: source venv/Scripts/activate"
echo "2. Run in voice mode: python main.py --mode voice"
echo "3. Run in text mode: python main.py --mode text"
echo "4. Run as server: python main.py --mode server"
echo ""
echo "For Android app:"
echo "1. Open android/MACAssistant in Android Studio"
echo "2. Build and install on your device"
echo "3. Enter your computer's IP address in the app"
