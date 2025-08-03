# MAC Assistant Documentation

This directory contains comprehensive documentation for the MAC (Multi-platform Assistant Core) voice assistant project.

## Documentation Index

### Getting Started
- [Installation Guide](installation.md) - Complete setup instructions for Windows and Android
- [Quick Start Guide](quickstart.md) - Get up and running in minutes
- [Configuration](configuration.md) - How to configure the assistant

### Architecture & Design
- [System Architecture](architecture.md) - High-level system design and components
- [API Documentation](api.md) - HTTP API endpoints and communication protocol
- [Voice Processing](voice-processing.md) - Speech recognition and synthesis details

### Development
- [Development Guide](development.md) - Setting up development environment
- [Contributing Guidelines](contributing.md) - How to contribute to the project
- [Testing Guide](testing.md) - Running and writing tests

### Platform-Specific
- [Windows Commands](windows-commands.md) - Detailed Windows command documentation
- [Android App](android-app.md) - Android application architecture and features

### Troubleshooting & Support
- [Troubleshooting Guide](troubleshooting.md) - Common issues and solutions
- [FAQ](faq.md) - Frequently asked questions
- [Changelog](changelog.md) - Version history and changes

### Advanced Topics
- [Security Considerations](security.md) - Security features and best practices
- [Performance Optimization](performance.md) - Tips for optimizing performance
- [Extending MAC](extending.md) - How to add new commands and features

## Project Overview

MAC is a cross-platform voice assistant that bridges Windows desktop environments with Android mobile devices through a sophisticated HTTP API communication system. The assistant features offline speech recognition, natural language command processing, and real-time synchronization between platforms.

### Key Features
- **Offline Speech Recognition** using Vosk models
- **Cross-Platform Communication** via HTTP API
- **Modular Command System** with platform-specific implementations
- **Real-Time Voice Processing** with audio feedback
- **Secure Local Network Communication** between devices
- **Extensible Architecture** for adding new commands and features

### Technology Stack
- **Backend**: Python 3.8+ with FastAPI, Vosk, pyttsx3
- **Frontend**: Android Kotlin with Jetpack Compose, Material Design 3
- **Communication**: HTTP REST API with CORS support
- **Audio**: PyAudio, Windows Audio APIs (pycaw), Android MediaRecorder
- **Architecture**: MVVM pattern, Repository pattern, Dependency injection

## Quick Reference

### Start the Assistant
```bash
# Voice mode (interactive)
python main.py --mode voice

# API server mode (for Android app)
python main.py --mode server

# Demo mode (command line testing)
python demo.py
```

### Basic Voice Commands
- "Hello MAC" - Greeting and status
- "What time is it?" - Current time and date
- "Volume up/down" - Audio control
- "System info" - Computer status
- "Network status" - Network information
- "Open calculator" - Launch applications

### Android App Features
- Voice input with visual feedback
- Real-time server communication
- Material Design 3 interface
- Command history and responses
- Network status monitoring

For detailed information, please refer to the specific documentation files listed above.
