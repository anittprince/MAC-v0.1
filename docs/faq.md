# Frequently Asked Questions (FAQ)

This FAQ covers the most commonly asked questions about the MAC Assistant system.

## General Questions

### What is MAC Assistant?

MAC is a cross-platform voice assistant that connects Windows desktop computers with Android mobile devices. It processes voice commands locally using offline speech recognition and can control various system functions.

**Key Features:**
- Offline voice recognition (no internet required for core functions)
- Cross-platform communication between Windows and Android
- System control (volume, applications, system info)
- Local network communication for privacy
- Extensible command system

### What platforms are supported?

**Currently Supported:**
- **Windows 10/11** (64-bit) - Full functionality
- **Android 8.0+** (API 26+) - Mobile interface

**Planned Support:**
- Linux distributions
- macOS
- iOS (future consideration)

### Is internet required?

**For Core Functions:** No internet required
- Voice recognition works offline using Vosk models
- System commands execute locally
- Local network communication only

**For Optional Features:**
- Weather information (requires API key)
- Software updates
- Additional voice model downloads

### Is my data private?

**Yes, privacy is a core design principle:**
- All voice processing happens locally on your device
- No data sent to external servers
- Communication stays within your local network
- No cloud dependencies for core functionality
- Voice commands are not stored or transmitted

## Installation and Setup

### What are the system requirements?

**Windows Requirements:**
- Windows 10 or 11 (64-bit)
- Python 3.8 or later
- 4GB RAM minimum (8GB recommended)
- 2GB free storage space
- Microphone and speakers/headphones
- Network adapter for Android communication

**Android Requirements:**
- Android 8.0+ (API level 26)
- 2GB RAM minimum
- 100MB free storage
- Microphone for voice input
- WiFi connection to same network as Windows PC

### How long does installation take?

**Typical Installation Times:**
- **Automated setup:** 5-10 minutes
- **Manual installation:** 15-30 minutes
- **Voice model download:** 2-5 minutes (40MB model)
- **Android app build:** 3-5 minutes

**Factors affecting time:**
- Internet connection speed
- Computer performance
- Antivirus software scanning

### Can I use MAC without Android?

**Yes!** MAC works perfectly as a Windows-only voice assistant:
- Use `python main.py --mode voice` for direct voice interaction
- All Windows commands work independently
- No Android device required for system control
- API server is optional

### Do I need Administrator privileges?

**For Installation:** Recommended but not always required
- Installing Python packages
- Setting up audio drivers
- Configuring Windows Firewall

**For Running:** Usually not required
- Basic voice commands work with standard user permissions
- Some system information queries may need elevated permissions
- Volume control typically works for standard users

## Usage and Commands

### What commands are available?

**Basic Commands:**
- `"Hello MAC"` - Greeting and status
- `"What time is it?"` - Current time and date
- `"Volume up/down"` - Audio control
- `"Mute/unmute"` - Audio muting
- `"System info"` - Computer status
- `"Network status"` - Network information
- `"Open [application]"` - Launch programs

**See [Windows Commands Documentation](windows-commands.md) for complete list.**

### How accurate is voice recognition?

**Recognition Accuracy:**
- **Small model:** 85-90% for basic commands
- **Large model:** 95-98% for clear speech
- **Factors affecting accuracy:**
  - Background noise level
  - Microphone quality
  - Speaking clarity and pace
  - Accent and pronunciation

**Tips for better recognition:**
- Speak clearly at normal pace
- Use a good quality microphone
- Minimize background noise
- Use consistent command phrasing

### Can I add custom commands?

**Yes!** The system is designed for extensibility:

**For Developers:**
- Add new patterns to `core/brain.py`
- Implement handlers in command modules
- Follow the existing command structure

**For Users:**
- Modify existing patterns for personal preferences
- Request new commands via feature requests
- Contribute to the project

### Why are some commands disabled?

**Safety and Security Reasons:**
- **Power commands** (shutdown, restart) - Prevent accidental system shutdown
- **File deletion** - Avoid data loss
- **System configuration** - Prevent system instability
- **Network changes** - Maintain connectivity

**These can be enabled** by modifying the source code if needed for advanced users.

## Technical Questions

### Which speech recognition engine is used?

**Vosk Speech Recognition:**
- **Technology:** Based on Kaldi ASR toolkit
- **Type:** Offline, local processing
- **Languages:** 20+ languages supported
- **Models:** Multiple sizes available (40MB to 1.8GB)
- **Performance:** Real-time recognition on modern hardware

**Why Vosk?**
- Offline operation (privacy)
- Good accuracy for voice commands
- Lightweight and fast
- Free and open source
- Cross-platform support

### How does Android communicate with Windows?

**Communication Method:**
- **Protocol:** HTTP REST API
- **Format:** JSON request/response
- **Network:** Local WiFi network only
- **Port:** 8000 (configurable)
- **Security:** Local network only, no external access

**Data Flow:**
1. Android app captures voice
2. Converts speech to text
3. Sends HTTP POST to Windows API
4. Windows processes command
5. Returns JSON response
6. Android displays/speaks result

### Can I change the voice or speech settings?

**Yes, voice output is customizable:**

**Voice Selection:**
```python
# In core/voice_output.py
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Female voice
```

**Speech Rate:**
```python
engine.setProperty('rate', 200)  # Words per minute
```

**Volume:**
```python
engine.setProperty('volume', 0.8)  # 0.0 to 1.0
```

### Why does voice recognition seem slow?

**Common Causes:**
- **Large model:** Using 1.8GB model instead of 40MB model
- **Hardware:** Insufficient CPU or RAM
- **Background processes:** Other apps using resources
- **Audio processing:** Real-time recognition overhead

**Performance Improvements:**
- Use vosk-model-small-en-us (40MB)
- Close unnecessary applications
- Use SSD storage for models
- Ensure adequate RAM (8GB recommended)

## Troubleshooting

### MAC says "I didn't understand that command"

**Common Causes:**
- Command not in recognized patterns
- Poor audio quality or background noise
- Microphone issues
- Speech too fast or unclear

**Solutions:**
1. **Check supported commands** in documentation
2. **Test microphone** with Windows Voice Recorder
3. **Speak clearly** and at normal pace
4. **Reduce background noise**
5. **Try rephrasing** the command

### Volume control doesn't work

**Most Common Issue:** Missing pycaw library

**Solution:**
```bash
pip install pycaw
```

**Other Causes:**
- No audio output device detected
- Audio drivers not installed
- Windows audio service not running
- Permission issues

**See [Troubleshooting Guide](troubleshooting.md) for detailed solutions.**

### Android app can't connect to Windows

**Step-by-step diagnosis:**

1. **Verify API server is running:**
   ```bash
   python main.py --mode server
   ```

2. **Check IP address:**
   ```bash
   ipconfig
   ```

3. **Test from browser:**
   Visit `http://your-ip:8000` on phone

4. **Check Windows Firewall:**
   Allow Python through firewall

5. **Verify same network:**
   Both devices on same WiFi

### Error: "No module named 'vosk'"

**Cause:** Dependencies not installed properly

**Solutions:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Install specific package
pip install vosk

# Use setup script
setup.bat
```

## Performance and Optimization

### How much resources does MAC use?

**Typical Resource Usage:**
- **CPU:** 5-15% during voice recognition
- **RAM:** 100-300MB depending on model size
- **Storage:** 100MB-2GB for voice models
- **Network:** Minimal, local traffic only

**Resource Spikes:**
- Higher CPU during active listening
- Memory spike when loading voice models
- Disk access when saving configuration

### Can I run MAC on older hardware?

**Minimum Specifications:**
- **CPU:** Dual-core 2GHz processor
- **RAM:** 4GB (8GB recommended)
- **Storage:** 2GB free space
- **OS:** Windows 10 (older versions may work)

**Optimization for Older Hardware:**
- Use small voice model (40MB)
- Close background applications
- Reduce recognition frequency
- Use push-to-talk instead of continuous listening

### How can I improve response speed?

**Optimization Tips:**
1. **Use smaller voice model** (40MB vs 1.8GB)
2. **SSD storage** for faster model loading
3. **Adequate RAM** to avoid swapping
4. **Close background apps** to free resources
5. **Good microphone** for faster recognition
6. **Wired connection** for Android communication

## Development and Customization

### Can I modify the source code?

**Yes!** MAC is open source:
- **License:** Check project license
- **Contributions:** Welcome via pull requests
- **Custom modifications:** Encouraged for personal use
- **Documentation:** Available for developers

### How do I add new voice commands?

**Basic Steps:**
1. **Add pattern** to `core/brain.py`
2. **Implement handler** in appropriate command module
3. **Test thoroughly**
4. **Update documentation**

**Example:**
```python
# In core/brain.py
elif 'weather' in text:
    return self.windows_commands.handle_weather(text)

# In commands/windows.py
def handle_weather(self, text: str) -> Dict[str, Any]:
    return {"message": "Weather feature coming soon!", "data": None}
```

### Can I port MAC to other platforms?

**Yes!** The architecture supports new platforms:
- **Create new command module** (e.g., `commands/linux.py`)
- **Implement platform-specific operations**
- **Register with the brain processor**
- **Test on target platform**

**Existing examples:**
- `commands/windows.py` for Windows
- `commands/android.py` for Android (partial)

### How do I contribute to the project?

**Ways to Contribute:**
1. **Bug reports** with detailed information
2. **Feature requests** with use cases
3. **Code contributions** via pull requests
4. **Documentation improvements**
5. **Testing** on different hardware/software configurations

**Before Contributing:**
- Read contribution guidelines
- Check existing issues and pull requests
- Test changes thoroughly
- Follow code style conventions

## Future Development

### What features are planned?

**Short-term (Next Version):**
- Weather integration
- Enhanced voice models
- Improved Android app features
- Better error handling

**Medium-term:**
- Linux support
- macOS support
- Voice model training tools
- Plugin system

**Long-term:**
- iOS support
- Home automation integration
- AI conversation capabilities
- Cloud synchronization (optional)

### Will MAC always be free?

**Yes!** MAC is committed to being:
- **Open source** - Source code always available
- **Free to use** - No licensing fees
- **Privacy-focused** - No data collection
- **Community-driven** - User and developer contributions welcome

### How often are updates released?

**Update Schedule:**
- **Bug fixes:** As needed
- **Minor updates:** Monthly
- **Major releases:** Quarterly
- **Security updates:** Immediate when needed

**Update Method:**
- Download new version from repository
- Backup configuration before updating
- Follow upgrade instructions in documentation

---

## Still Have Questions?

### Documentation Resources
- [Installation Guide](installation.md)
- [Quick Start Guide](quickstart.md)
- [Troubleshooting Guide](troubleshooting.md)
- [API Documentation](api.md)

### Community Support
- Project repository issues
- Community discussions
- Developer forums
- User guides and tutorials

### Reporting Issues
- Search existing issues first
- Provide detailed problem description
- Include system information and logs
- Follow issue template guidelines
