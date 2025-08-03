# Troubleshooting Guide

This guide helps you diagnose and fix common issues with the MAC Assistant system.

## Quick Diagnostic Steps

### 1. System Check
```bash
python test_mac.py
```
This verifies all core components are working correctly.

### 2. Environment Verification
```bash
python -c "import vosk, pyttsx3, fastapi, pycaw; print('All modules imported successfully')"
```

### 3. Audio Hardware Test
```bash
python -c "import pyaudio; print('Audio available:', pyaudio.PyAudio().get_device_count())"
```

## Common Issues and Solutions

### Installation Problems

#### Error: "Python not found"
**Symptoms:** Command prompt doesn't recognize `python`

**Solutions:**
1. **Install Python 3.8+** from [python.org](https://python.org)
2. **Add to PATH** during installation
3. **Restart Command Prompt** after installation
4. **Use `py` instead of `python`** on some Windows systems

#### Error: "pip not found"
**Symptoms:** `pip install` commands fail

**Solutions:**
```bash
# Reinstall pip
python -m ensurepip --upgrade

# Use py launcher
py -m pip install package_name

# Manual pip installation
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

#### Error: "Microsoft Visual C++ 14.0 is required"
**Symptoms:** Packages fail to install during compilation

**Solutions:**
1. **Install Visual Studio Build Tools**
   - Download from Microsoft
   - Select C++ build tools
   - Restart system

2. **Use pre-compiled wheels**
   ```bash
   pip install --only-binary=all package_name
   ```

### Voice Recognition Issues

#### Error: "No Default Input Device Available"
**Symptoms:** Voice input fails to initialize

**Diagnosis:**
```bash
python -c "
import pyaudio
pa = pyaudio.PyAudio()
for i in range(pa.get_device_count()):
    info = pa.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f'Input Device {i}: {info[\"name\"]}')
"
```

**Solutions:**
1. **Check Microphone Connection**
   - Ensure microphone is plugged in
   - Test with Windows Voice Recorder
   - Check Device Manager for audio devices

2. **Set Default Recording Device**
   - Right-click sound icon in system tray
   - Select "Recording devices"
   - Set microphone as default

3. **Install Audio Drivers**
   - Update audio drivers from Device Manager
   - Install manufacturer's audio software
   - Restart system

4. **PyAudio Reinstallation**
   ```bash
   pip uninstall pyaudio
   pip install pyaudio
   ```

#### Error: "Vosk model not found"
**Symptoms:** Speech recognition fails to start

**Solutions:**
1. **Download Vosk Model**
   ```bash
   mkdir models
   cd models
   # Download from https://alphacephei.com/vosk/models
   # Extract vosk-model-small-en-us-0.15.zip to models/vosk-model/
   ```

2. **Verify Model Structure**
   ```
   models/
   └── vosk-model/
       ├── am/
       ├── graph/
       ├── ivector/
       ├── conf/
       └── README
   ```

3. **Alternative Model Path**
   ```bash
   python main.py --model-path "path/to/your/model"
   ```

#### Poor Recognition Accuracy
**Symptoms:** Commands not recognized correctly

**Solutions:**
1. **Check Audio Quality**
   - Use noise-canceling microphone
   - Minimize background noise
   - Speak clearly and at normal pace

2. **Adjust Microphone Settings**
   - Increase microphone levels
   - Enable noise suppression
   - Disable audio enhancements that might interfere

3. **Use Larger Model**
   - Download vosk-model-en-us-0.22 (1.8GB)
   - Better accuracy but slower processing

### Volume Control Issues

#### Error: "Volume control requires pycaw library"
**Symptoms:** Volume commands don't work

**Solutions:**
```bash
pip install pycaw
```

#### Error: "No audio endpoint found"
**Symptoms:** pycaw fails to find audio devices

**Solutions:**
1. **Restart Windows Audio Service**
   ```cmd
   net stop audiosrv
   net start audiosrv
   ```

2. **Check Audio Devices**
   - Ensure speakers/headphones are connected
   - Set as default playback device
   - Test audio output

3. **Run as Administrator**
   ```cmd
   # Run Command Prompt as Administrator
   python main.py --mode voice
   ```

#### Error: "COM interface error"
**Symptoms:** Volume control crashes with COM errors

**Solutions:**
1. **Reinstall comtypes**
   ```bash
   pip uninstall comtypes
   pip install comtypes
   ```

2. **Clear COM Cache**
   ```python
   import comtypes
   comtypes.client.GetModule("path/to/com/library")
   ```

### API Server Issues

#### Error: "Port 8000 already in use"
**Symptoms:** API server fails to start

**Diagnosis:**
```bash
netstat -ano | findstr :8000
```

**Solutions:**
1. **Use Different Port**
   ```bash
   python main.py --mode server --port 8001
   ```

2. **Kill Process Using Port**
   ```cmd
   # Find PID from netstat output
   taskkill /PID <PID> /F
   ```

3. **Change Default Port**
   - Edit `sync/api.py`
   - Change `DEFAULT_PORT = 8000` to different value

#### Error: "Permission denied binding to port"
**Symptoms:** Can't bind to network interface

**Solutions:**
1. **Run as Administrator**
   ```cmd
   # Right-click Command Prompt → Run as Administrator
   python main.py --mode server
   ```

2. **Use Localhost Only**
   ```bash
   python main.py --mode server --host 127.0.0.1
   ```

3. **Configure Windows Firewall**
   - Add Python to firewall exceptions
   - Allow port 8000 through firewall

### Android App Issues

#### Error: "Cannot connect to server"
**Symptoms:** Android app can't reach Windows PC

**Diagnosis:**
1. **Test Network Connectivity**
   ```bash
   ping <windows-ip>
   ```

2. **Test API Endpoint**
   ```bash
   curl http://<windows-ip>:8000/
   ```

**Solutions:**
1. **Verify IP Address**
   ```bash
   ipconfig
   # Use IPv4 address from active network adapter
   ```

2. **Check Same Network**
   - Ensure both devices on same WiFi
   - Disable VPN on either device
   - Check router settings

3. **Windows Firewall Configuration**
   ```cmd
   # Allow Python through firewall
   netsh advfirewall firewall add rule name="MAC Assistant" dir=in action=allow program="C:\Path\To\Python\python.exe"
   
   # Or allow port
   netsh advfirewall firewall add rule name="MAC API" dir=in action=allow protocol=TCP localport=8000
   ```

4. **Test with Browser**
   - Open browser on Android
   - Visit `http://<windows-ip>:8000`
   - Should see "MAC Assistant API is running"

#### Android App Crashes
**Symptoms:** App closes unexpectedly

**Solutions:**
1. **Check Android Logs**
   ```bash
   adb logcat | grep MACAssistant
   ```

2. **Permissions Check**
   - Ensure microphone permission granted
   - Check network access permission

3. **Rebuild App**
   - Clean project in Android Studio
   - Rebuild and reinstall

### Performance Issues

#### Slow Response Times
**Symptoms:** Commands take long time to process

**Solutions:**
1. **Use Smaller Vosk Model**
   - vosk-model-small-en-us-0.15 (40MB)
   - Faster but less accurate

2. **Close Background Apps**
   - Free up CPU and memory
   - Check Task Manager for resource usage

3. **SSD Storage**
   - Move models to SSD for faster loading
   - Ensure adequate free space

#### High CPU Usage
**Symptoms:** System becomes slow during voice processing

**Solutions:**
1. **Monitor Resource Usage**
   ```bash
   python -c "
   import psutil
   print(f'CPU: {psutil.cpu_percent()}%')
   print(f'Memory: {psutil.virtual_memory().percent}%')
   "
   ```

2. **Adjust Recognition Interval**
   - Modify voice input polling frequency
   - Use push-to-talk instead of continuous listening

3. **Voice Processing Optimization**
   ```python
   # In voice_input.py, adjust recognition parameters
   recognizer.energy_threshold = 4000  # Higher threshold
   recognizer.pause_threshold = 1.0    # Longer pause detection
   ```

## Advanced Troubleshooting

### Debug Mode

Enable detailed logging:
```bash
python main.py --mode voice --debug
```

This provides verbose output for diagnosing issues.

### Manual Testing

#### Test Individual Components

**Voice Output:**
```python
from core.voice_output import VoiceOutput
vo = VoiceOutput()
vo.speak("Testing voice output")
```

**Voice Input:**
```python
from core.voice_input import VoiceInput
vi = VoiceInput("models/vosk-model")
print("Say something...")
result = vi.listen()
print(f"Heard: {result}")
```

**Windows Commands:**
```python
from commands.windows import WindowsCommands
wc = WindowsCommands()
result = wc.handle_time("what time is it")
print(result)
```

### Log Analysis

#### Enable Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Common Log Messages
- `"Model loading failed"` - Vosk model issues
- `"Audio device not found"` - Hardware problems
- `"Permission denied"` - Security/admin issues
- `"Connection refused"` - Network problems

### Environment Cleanup

#### Reset Python Environment
```bash
# Deactivate virtual environment
deactivate

# Remove and recreate
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### Clear Audio Cache
```cmd
# Stop audio services
net stop audiosrv
net stop audioendpointbuilder

# Start audio services
net start audioendpointbuilder
net start audiosrv
```

### System Requirements Check

#### Minimum Requirements
- **OS:** Windows 10 (64-bit)
- **Python:** 3.8+
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 2GB free space
- **Audio:** Microphone and speakers

#### Hardware Compatibility
```python
import platform, psutil
print(f"OS: {platform.system()} {platform.release()}")
print(f"Python: {platform.python_version()}")
print(f"RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
print(f"CPU: {psutil.cpu_count()} cores")
```

## Getting Additional Help

### Collect Diagnostic Information

When reporting issues, include:
```bash
# System information
python -c "
import platform, sys, psutil
print(f'OS: {platform.system()} {platform.release()}')
print(f'Python: {sys.version}')
print(f'CPU: {psutil.cpu_count()} cores')
print(f'RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB')
"

# Installed packages
pip list

# MAC test results
python test_mac.py
```

### Log Files

Important log locations:
- **Windows Event Logs:** Event Viewer → Windows Logs
- **Python Errors:** Console output or redirected to file
- **Audio Logs:** Windows → Settings → System → Sound → Troubleshoot

### Support Resources

1. **Documentation:** Read related docs for specific features
2. **Community:** Check project discussions and issues
3. **Bug Reports:** Submit detailed issue reports
4. **Feature Requests:** Suggest improvements or new features

### Emergency Recovery

#### Complete Reset
```bash
# Save any custom configurations
# Then remove and reinstall everything
rmdir /s MAC-v0.1
# Download fresh copy
# Run setup.bat
```

This should resolve most persistent issues by starting with a clean installation.
