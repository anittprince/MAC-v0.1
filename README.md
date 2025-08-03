# MAC - Cross-Platform Voice Assistant

A cross-platform voice assistant that works on Windows and Android, featuring voice input/output, command processing, HTTP API communication, and **AI integration** for answering general questions.

## Features

- **Voice Input/Output**: Uses Vosk for speech recognition and pyttsx3 for text-to-speech
- **🤖 AI Integration**: ChatGPT integration, web search, and YouTube search capabilities
- **Cross-Platform**: Supports Windows and Android
- **HTTP API**: FastAPI server for remote command execution
- **Modular Design**: Separate command modules for different platforms
- **Real-time Communication**: Android app communicates with Python server over LAN
- **Smart Fallback**: Graceful degradation from predefined commands to AI responses

## New AI Capabilities

🎉 **MAC now includes powerful AI features:**

- **ChatGPT Integration**: Ask any general question and get intelligent responses
- **Web Search**: Search for information using "search for [topic]" or "what is [something]"
- **YouTube Search**: Find videos with "youtube [topic]" or "find video about [topic]"
- **Weather Information**: Get weather updates (requires API key)
- **Smart Fallback**: If MAC doesn't understand a command, it tries to answer using AI

**Examples:**
```
User: "what is machine learning"
MAC: "Machine learning is a subset of artificial intelligence..."

User: "search for latest Python frameworks"
MAC: "I found information about latest Python frameworks..."

User: "youtube cooking tutorials"
MAC: "I found 3 YouTube videos for 'cooking tutorials'..."
```

See [`docs/AI_INTEGRATION.md`](docs/AI_INTEGRATION.md) for detailed setup instructions.

## Project Structure

```
MAC-v0.1/
├── core/
│   ├── __init__.py
│   ├── brain.py          # Main command processor with AI integration
│   ├── voice_input.py    # Voice recognition
│   ├── voice_output.py   # Text-to-speech
│   └── ai_services.py    # AI services (ChatGPT, search, YouTube)
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
├── docs/
│   ├── AI_INTEGRATION.md    # AI setup and usage guide
│   ├── API.md               # API documentation
│   └── [other docs...]      # Additional documentation
├── main.py              # Main entry point
├── test_mac.py          # Quick test script
├── test_ai.py           # AI integration test script
├── .env.template        # Environment variables template
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
