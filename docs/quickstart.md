# Quick Start Guide

Get up and running with MAC Assistant in minutes! This guide will walk you through the essential steps to start using your cross-platform voice assistant.

## Prerequisites Check

Before starting, ensure you have:
- **Windows 10/11** (64-bit)
- **Python 3.8+** installed
- **Microphone and speakers** connected
- **Android device** (for mobile features)
- **Local network connection** (WiFi)

## Quick Installation

### Step 1: Download and Extract
1. Download the MAC Assistant project
2. Extract to a folder like `C:\MAC-Assistant\`
3. Open Command Prompt or PowerShell in the project folder

### Step 2: Automated Setup
Run the setup script:
```batch
setup.bat
```

This will:
- Create Python virtual environment
- Install all dependencies
- Verify installation
- Download speech model (if available)

### Step 3: Verify Installation
```bash
python test_mac.py
```

You should see:
```
✓ Core modules import successfully
✓ Voice output initialized
✓ System commands working
✓ API server can start
✓ All tests passed!
```

## First Run

### Start Voice Mode
```bash
python main.py --mode voice
```

**Try these commands:**
- "Hello MAC"
- "What time is it?"
- "Volume up"
- "System info"

### Start API Server (for Android)
```bash
python main.py --mode server
```

The server will start on `http://your-ip:8000`

## Basic Voice Commands

### Essential Commands

| Command | What It Does | Example Response |
|---------|--------------|------------------|
| `"Hello MAC"` | Greeting with time-aware response | "Good afternoon, User! How can I help?" |
| `"What time is it?"` | Current time and date | "The current time is 2:30 PM on Monday..." |
| `"Volume up"` | Increase system volume by 10% | "Volume increased to 75%" |
| `"Volume down"` | Decrease system volume by 10% | "Volume decreased to 65%" |
| `"Mute"` | Mute system audio | "Volume muted" |
| `"System info"` | Computer status | "System Status: CPU 15%, RAM 68%..." |
| `"Network status"` | Network information | "Network Status: Connected. Found 3 interfaces..." |
| `"Open calculator"` | Launch Windows Calculator | "Opening calc.exe" |

### Getting Help
Say: `"Help"` or `"What can you do?"` for available commands.

## Android App Setup

### Build the App
1. Install **Android Studio**
2. Open `android/MACAssistant` project
3. Build and install on your device

### Configure Connection
1. Find your Windows PC IP address:
   ```bash
   ipconfig
   ```
2. In Android app settings, enter the IP address
3. Set port to `8000`
4. Test connection

### Use Android App
1. Start API server on Windows: `python main.py --mode server`
2. Open MAC Assistant app on Android
3. Tap microphone button
4. Speak your command
5. See response on phone and hear it on PC

## Quick Demo

### Test Basic Functionality
```bash
python demo.py
```

This runs a quick demonstration of core features.

### Voice Command Test
1. Start voice mode: `python main.py --mode voice`
2. Wait for "Listening..." prompt
3. Say: "Hello MAC"
4. Listen for response
5. Try: "What time is it?"

### API Test
1. Start server: `python main.py --mode server`
2. Open browser to: `http://localhost:8000/docs`
3. Try the `/command` endpoint with text: "system info"

## Common Usage Patterns

### Morning Routine
```
"Good morning MAC"
"What time is it?"
"System info"
"Network status"
```

### Work Session
```
"Open calculator"
"Volume down"
"What's running?"
"Current volume"
```

### System Check
```
"System info"
"Network status"
"Show files"
"Check connection"
```

## Troubleshooting Quick Fixes

### No Voice Recognition
1. Check microphone connection
2. Ensure microphone is default recording device
3. Test with Windows Voice Recorder
4. Restart MAC Assistant

### Volume Control Not Working
```bash
pip install pycaw
```

### API Server Won't Start
1. Check if port 8000 is free
2. Run as administrator
3. Check Windows Firewall settings

### Android Can't Connect
1. Verify IP address is correct
2. Ensure both devices on same WiFi
3. Check Windows Firewall allows Python
4. Test with browser: `http://your-ip:8000`

## Performance Tips

### Optimize Voice Recognition
- Use a good quality microphone
- Minimize background noise
- Speak clearly and at normal pace
- Keep commands concise

### Improve Response Time
- Use small Vosk model for faster processing
- Close unnecessary applications
- Ensure good network connection

### Battery Optimization (Android)
- Don't keep app running continuously
- Use push-to-talk feature
- Close app when not needed

## What's Next?

### Explore Advanced Features
- Read [Windows Commands Documentation](windows-commands.md)
- Learn about [API Integration](api.md)
- Understand [System Architecture](architecture.md)

### Customize Your Experience
- Modify voice recognition settings
- Add custom commands
- Configure network settings
- Adjust audio preferences

### Development and Extension
- Read [Development Guide](development.md)
- Check [Contributing Guidelines](contributing.md)
- Explore [Extension Framework](extending.md)

## Quick Reference Card

### Start Commands
```bash
# Voice mode
python main.py --mode voice

# API server
python main.py --mode server

# Demo
python demo.py

# Test
python test_mac.py
```

### Essential Voice Commands
- Greeting: `"Hello MAC"`
- Time: `"What time is it?"`
- Volume: `"Volume up/down"`, `"Mute"`
- System: `"System info"`
- Apps: `"Open calculator"`
- Network: `"Network status"`

### Keyboard Shortcuts (Voice Mode)
- `Ctrl+C` - Stop listening and exit
- `Space` - Manual trigger (if continuous listening disabled)
- `Enter` - Skip current recognition

### API Endpoints
- Health: `GET /`
- Command: `POST /command`
- Status: `GET /status`
- Docs: `GET /docs`

## Need Help?

### Documentation
- [Installation Guide](installation.md) - Detailed setup instructions
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
- [FAQ](faq.md) - Frequently asked questions

### Support Channels
- Check project repository for issues
- Read community discussions
- Submit bug reports with logs

### Diagnostic Information
When reporting issues, include:
- Windows version
- Python version
- Error messages
- Steps to reproduce
- Audio hardware details

---

**Congratulations!** You're now ready to use MAC Assistant. Start with basic commands and gradually explore more advanced features as you become comfortable with the system.
