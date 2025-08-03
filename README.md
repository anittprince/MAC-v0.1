# MAC - Cross-Platform Voice Assistant

A cross-platform voice assistant that works on Windows and Android, featuring voice input/output, command processing, and HTTP API communication.

## Features

- **Voice Input/Output**: Uses Vosk for speech recognition and pyttsx3 for text-to-speech
- **Cross-Platform**: Supports Windows and Android
- **HTTP API**: FastAPI server for remote command execution
- **Modular Design**: Separate command modules for different platforms
- **Real-time Communication**: Android app communicates with Python server over LAN

## Project Structure

```
MAC-v0.1/
├── core/
│   ├── __init__.py
│   ├── brain.py          # Main command processor
│   ├── voice_input.py    # Voice recognition
│   └── voice_output.py   # Text-to-speech
├── commands/
│   ├── __init__.py
│   ├── windows.py        # Windows-specific commands
│   └── android.py        # Android-specific commands
├── sync/
│   ├── __init__.py
│   └── api.py           # FastAPI server
├── android/
│   └── MACAssistant/    # Android Kotlin app
│       ├── app/
│       │   ├── src/main/java/com/mac/assistant/
│       │   │   ├── MainActivity.kt
│       │   │   ├── viewmodel/AssistantViewModel.kt
│       │   │   ├── model/ApiModels.kt
│       │   │   ├── network/ApiService.kt
│       │   │   ├── repository/AssistantRepository.kt
│       │   │   ├── service/VoiceManager.kt
│       │   │   └── ui/screens/MainScreen.kt
│       │   └── build.gradle.kts
│       ├── build.gradle
│       └── settings.gradle.kts
├── main.py              # Main entry point
├── test_mac.py          # Quick test script
├── setup.bat            # Windows setup script
├── setup.sh             # Linux/Mac setup script
├── requirements.txt     # Python dependencies
└── requirements-windows.txt  # Windows-specific dependencies
```

## Setup

### Quick Setup (Windows)

1. Run the setup script:
```cmd
setup.bat
```

### Manual Setup

#### Python Environment

1. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
# On Windows, also install:
pip install -r requirements-windows.txt
```

3. Download Vosk model for offline speech recognition:
   - Go to https://alphacephei.com/vosk/models
   - Download `vosk-model-small-en-us-0.15.zip`
   - Extract to `models/vosk-model/`

#### Android App

1. Open `android/MACAssistant` in Android Studio
2. Build and install on your Android device
3. Ensure both devices are on the same network

## Usage

### Testing the Core (Without Voice)

```bash
python test_mac.py
```

### Running the Assistant

#### Voice Mode (Default)
```bash
python main.py --mode voice
```

#### Text Mode (No microphone required)
```bash
python main.py --mode text
```

#### Server Mode (For Android app)
```bash
python main.py --mode server
# Server runs on http://0.0.0.0:8000
```

### Android App

1. Launch the MAC Assistant app
2. Enter the IP address of your Python server (e.g., `192.168.1.100:8000`)
3. Test the connection
4. Use voice commands through the app

## API Endpoints

- `POST /command` - Send text command and receive response
- `GET /health` - Health check endpoint

## Supported Commands

### Windows
- System information
- File operations
- Application control
- Network status

### Android
- Device information
- Notification management
- System settings

## License

MIT License
