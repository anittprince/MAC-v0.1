# Installation Guide

This guide provides step-by-step instructions for installing and setting up the MAC Assistant on both Windows and Android platforms.

## Prerequisites

### System Requirements

#### Windows
- **Operating System**: Windows 10 or later (64-bit)
- **Python**: Python 3.8 or later
- **RAM**: Minimum 4GB, recommended 8GB
- **Storage**: At least 2GB free space for models and dependencies
- **Audio**: Microphone and speakers/headphones
- **Network**: Local network access for Android communication

#### Android
- **Operating System**: Android 8.0 (API level 26) or later
- **Storage**: At least 100MB free space
- **RAM**: Minimum 2GB
- **Audio**: Microphone for voice input
- **Network**: WiFi connection to same network as Windows PC

### Required Software

#### Windows
- **Python 3.8+**: Download from [python.org](https://www.python.org/downloads/)
- **Git** (optional): For cloning the repository
- **Text Editor/IDE**: VS Code, PyCharm, or similar

#### Android
- **Android Studio**: For building the Android app
- **Java Development Kit (JDK) 11+**: Required by Android Studio

## Installation Steps

### Step 1: Get the Source Code

#### Option A: Download ZIP
1. Download the project ZIP file
2. Extract to your desired location (e.g., `C:\MAC-Assistant\`)

#### Option B: Clone Repository
```bash
git clone <repository-url>
cd MAC-v0.1
```

### Step 2: Windows Backend Setup

#### Automated Setup (Recommended)
1. Navigate to the project directory
2. Run the setup script:
```batch
setup.bat
```

This script will:
- Create a Python virtual environment
- Install all required dependencies
- Download the Vosk speech model (if available)
- Verify the installation

#### Manual Setup
If the automated setup fails, follow these manual steps:

1. **Create Virtual Environment**
```bash
python -m venv venv
venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-windows.txt
```

3. **Download Speech Model**
```bash
# Create models directory
mkdir models
cd models

# Download Vosk model (approximately 40MB)
# Visit https://alphacephei.com/vosk/models
# Download vosk-model-small-en-us-0.15.zip
# Extract to models/vosk-model/
```

#### Dependency Details

**Core Dependencies:**
- `fastapi` - Web API framework
- `uvicorn` - ASGI server
- `vosk` - Speech recognition
- `pyttsx3` - Text-to-speech
- `pyaudio` - Audio input/output
- `psutil` - System information
- `requests` - HTTP client

**Windows-Specific:**
- `pycaw` - Audio control
- `pywin32` - Windows API access
- `comtypes` - COM interface support

### Step 3: Verify Installation

Run the verification script:
```bash
python test_mac.py
```

Expected output:
```
Testing MAC Assistant Components...

✓ Core modules import successfully
✓ Voice output initialized
✓ System commands working
✓ API server can start
✓ All tests passed!

MAC Assistant is ready to use.
```

### Step 4: Android App Setup

#### Prerequisites
1. Install Android Studio
2. Install JDK 11 or later
3. Set up Android SDK

#### Build Process
1. Open Android Studio
2. Select "Open an existing project"
3. Navigate to `android/MACAssistant`
4. Wait for Gradle sync to complete
5. Connect your Android device or start an emulator
6. Click "Run" or press Ctrl+R

#### APK Installation
If you have a pre-built APK:
1. Enable "Unknown sources" in Android settings
2. Transfer APK to device
3. Install the APK file

### Step 5: Network Configuration

#### Find Windows PC IP Address
```bash
ipconfig
```
Look for your local IP address (e.g., 192.168.1.100)

#### Configure Android App
1. Open the MAC Assistant app
2. Go to Settings
3. Enter the Windows PC IP address
4. Set port to 8000 (default)
5. Test connection

## Post-Installation Setup

### Voice Model Configuration

#### Download Offline Model (Recommended)
1. Visit [Vosk Models](https://alphacephei.com/vosk/models)
2. Download `vosk-model-small-en-us-0.15.zip` (40MB)
3. Extract to `models/vosk-model/`

#### Alternative Models
- **Small Model** (40MB): Fast, good for basic commands
- **Large Model** (1.8GB): Better accuracy, slower processing
- **Other Languages**: Available for multiple languages

### Audio Configuration

#### Windows Audio Setup
1. Ensure microphone is working
2. Set microphone as default recording device
3. Adjust microphone levels in Windows sound settings
4. Test with Windows Voice Recorder

#### Troubleshooting Audio
- **No microphone detected**: Check device manager
- **Audio quality poor**: Adjust microphone sensitivity
- **Background noise**: Use noise cancellation software

### Firewall Configuration

#### Windows Firewall
The API server runs on port 8000. Add firewall exception:
1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Add Python.exe with public network access
4. Or add port 8000 manually

#### Router Configuration
For cross-device communication:
- Ensure devices are on same WiFi network
- Check router firewall settings
- Test connectivity with ping

## Verification Tests

### Test Voice Recognition
```bash
python main.py --mode voice
```
Say: "Hello MAC" - Should respond with greeting

### Test API Server
```bash
python main.py --mode server
```
Visit: http://localhost:8000/docs - Should show API documentation

### Test Android Connection
1. Start API server on Windows
2. Open Android app
3. Say "What time is it?"
4. Should receive time from Windows PC

## Common Installation Issues

### Python Module Errors
**Error**: `ModuleNotFoundError: No module named 'vosk'`
**Solution**: 
```bash
pip install vosk
```

### Audio Issues
**Error**: `OSError: No Default Input Device Available`
**Solution**: 
- Check microphone connection
- Install audio drivers
- Run Windows audio troubleshooter

### Network Connection
**Error**: Android app can't connect to server
**Solution**:
- Verify IP address is correct
- Check Windows firewall
- Ensure both devices on same network

### Permission Errors
**Error**: `PermissionError: [WinError 5] Access is denied`
**Solution**:
- Run command prompt as administrator
- Check antivirus software
- Verify Python installation permissions

## Advanced Configuration

### Custom Voice Models
To use different Vosk models:
1. Download model from Vosk website
2. Extract to `models/` directory
3. Update model path in configuration

### API Configuration
Modify `sync/api.py` for:
- Different port numbers
- CORS settings
- Authentication (if needed)

### Voice Settings
Customize in `core/voice_output.py`:
- Speech rate
- Voice selection
- Volume levels

## Environment Variables

Optional environment variables:
```bash
# Voice model path
export VOSK_MODEL_PATH=models/vosk-model

# API server host/port
export MAC_HOST=0.0.0.0
export MAC_PORT=8000

# Voice settings
export VOICE_RATE=200
export VOICE_VOLUME=0.8
```

## Development Setup

For development and contribution:

1. **Install Development Dependencies**
```bash
pip install pytest black flake8 mypy
```

2. **Pre-commit Hooks**
```bash
pip install pre-commit
pre-commit install
```

3. **Testing Framework**
```bash
pytest tests/
```

4. **Code Formatting**
```bash
black .
flake8 .
```

## Next Steps

After successful installation:
1. Read the [Quick Start Guide](quickstart.md)
2. Review [Available Commands](windows-commands.md)
3. Explore [API Documentation](api.md)
4. Check [Troubleshooting Guide](troubleshooting.md) if needed

## Support

If you encounter issues:
1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Review [FAQ](faq.md)
3. Submit an issue on the project repository
4. Join the community discussion forum
