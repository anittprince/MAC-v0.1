# Android App Documentation

This document provides comprehensive information about the MAC Assistant Android application, including architecture, features, setup, and development guidelines.

## Overview

The MAC Assistant Android app serves as a mobile interface for the Windows-based voice assistant system. It provides voice input capabilities, real-time communication with the Windows backend, and a modern Material Design 3 user interface.

**Key Features:**
- Voice input with visual feedback
- Real-time server communication via HTTP API
- Material Design 3 interface with Jetpack Compose
- MVVM architecture with Repository pattern
- Network status monitoring and error handling
- Command history and response display

## Architecture

### MVVM Pattern Implementation

The Android app follows the Model-View-ViewModel (MVVM) architectural pattern for clean separation of concerns and testability.

```
┌─────────────────────────────────────────────────────────────┐
│                    Android App Architecture                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────────────────────┐  │
│  │       View      │    │           ViewModel             │  │
│  │   (Compose UI)  │◄──►│    (State Management)           │  │
│  │                 │    │                                 │  │
│  │  ┌───────────┐  │    │  ┌─────────────────────────────┐│  │
│  │  │MainScreen │  │    │  │   AssistantViewModel        ││  │
│  │  └───────────┘  │    │  └─────────────────────────────┘│  │
│  │                 │    │                                 │  │
│  │  ┌───────────┐  │    │  ┌─────────────────────────────┐│  │
│  │  │Components │  │    │  │      UI State              ││  │
│  │  └───────────┘  │    │  └─────────────────────────────┘│  │
│  └─────────────────┘    └─────────────────────────────────┘  │
│           │                            │                     │
│           └──────────┬─────────────────┘                     │
│                      │                                       │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                 Repository Layer                        │  │
│  │                                                         │  │
│  │  ┌─────────────────────────────────────────────────────┐│  │
│  │  │            AssistantRepository                      ││  │
│  │  └─────────────────────────────────────────────────────┘│  │
│  └─────────────────────────────────────────────────────────┘  │
│                              │                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                 Network Layer                           │  │
│  │                                                         │  │
│  │  ┌───────────────┐    ┌─────────────────────────────────┐│  │
│  │  │   ApiService  │    │          Data Models           ││  │
│  │  │   (Retrofit)  │    │     (Request/Response)         ││  │
│  │  └───────────────┘    └─────────────────────────────────┘│  │
│  └─────────────────────────────────────────────────────────┘  │
│                              │                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                 Service Layer                           │  │
│  │                                                         │  │
│  │  ┌───────────────┐    ┌─────────────────────────────────┐│  │
│  │  │  VoiceManager │    │       Other Services           ││  │
│  │  │ (MediaRecorder)│    │                               ││  │
│  │  └───────────────┘    └─────────────────────────────────┘│  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

### Android Studio Project Layout

```
android/MACAssistant/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/mac/assistant/
│   │   │   │   ├── MainActivity.kt                 # Main activity
│   │   │   │   ├── AssistantApplication.kt         # Application class
│   │   │   │   ├── di/                            # Dependency Injection
│   │   │   │   │   └── AppModule.kt
│   │   │   │   ├── viewmodel/                     # ViewModels
│   │   │   │   │   └── AssistantViewModel.kt
│   │   │   │   ├── model/                         # Data Models
│   │   │   │   │   ├── ApiModels.kt
│   │   │   │   │   └── UiState.kt
│   │   │   │   ├── network/                       # Network Layer
│   │   │   │   │   ├── ApiService.kt
│   │   │   │   │   └── NetworkModule.kt
│   │   │   │   ├── repository/                    # Repository Layer
│   │   │   │   │   └── AssistantRepository.kt
│   │   │   │   ├── service/                       # Services
│   │   │   │   │   └── VoiceManager.kt
│   │   │   │   └── ui/                           # UI Components
│   │   │   │       ├── screens/
│   │   │   │       │   └── MainScreen.kt
│   │   │   │       ├── components/
│   │   │   │       │   ├── VoiceButton.kt
│   │   │   │       │   ├── ResponseCard.kt
│   │   │   │       │   └── StatusIndicator.kt
│   │   │   │       └── theme/
│   │   │   │           ├── Color.kt
│   │   │   │           ├── Theme.kt
│   │   │   │           └── Type.kt
│   │   │   ├── res/                              # Resources
│   │   │   │   ├── values/
│   │   │   │   │   ├── colors.xml
│   │   │   │   │   ├── strings.xml
│   │   │   │   │   └── themes.xml
│   │   │   │   ├── drawable/                     # Icons and graphics
│   │   │   │   └── mipmap/                       # App icons
│   │   │   └── AndroidManifest.xml               # App manifest
│   │   ├── test/                                 # Unit tests
│   │   └── androidTest/                          # Instrumentation tests
│   ├── build.gradle.kts                          # App build script
│   └── proguard-rules.pro                        # ProGuard rules
├── build.gradle                                   # Project build script
├── gradle.properties                              # Gradle properties
└── settings.gradle.kts                           # Project settings
```

## Key Components

### 1. MainActivity (`MainActivity.kt`)

The main entry point of the Android application.

```kotlin
package com.mac.assistant

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.mac.assistant.ui.screens.MainScreen
import com.mac.assistant.ui.theme.MACAssistantTheme
import com.mac.assistant.viewmodel.AssistantViewModel
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    
    private val viewModel: AssistantViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        setContent {
            MACAssistantTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    MainScreen(viewModel = viewModel)
                }
            }
        }
    }
}
```

### 2. AssistantViewModel (`viewmodel/AssistantViewModel.kt`)

Manages UI state and business logic for the assistant interface.

```kotlin
package com.mac.assistant.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mac.assistant.model.AssistantUiState
import com.mac.assistant.model.CommandResponse
import com.mac.assistant.repository.AssistantRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AssistantViewModel @Inject constructor(
    private val repository: AssistantRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(AssistantUiState())
    val uiState: StateFlow<AssistantUiState> = _uiState.asStateFlow()
    
    fun executeCommand(text: String) {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(
                    isLoading = true,
                    error = null
                )
                
                val response = repository.executeCommand(text)
                
                _uiState.value = _uiState.value.copy(
                    lastCommand = text,
                    lastResponse = response,
                    isLoading = false,
                    commandHistory = _uiState.value.commandHistory + 
                        Pair(text, response)
                )
                
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    error = e.message ?: "Unknown error occurred",
                    isLoading = false
                )
            }
        }
    }
    
    fun updateServerAddress(address: String) {
        _uiState.value = _uiState.value.copy(serverAddress = address)
        repository.updateServerAddress(address)
    }
    
    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
    
    fun testConnection() {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isTestingConnection = true)
                
                val isConnected = repository.testConnection()
                
                _uiState.value = _uiState.value.copy(
                    isConnected = isConnected,
                    isTestingConnection = false
                )
                
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isConnected = false,
                    isTestingConnection = false,
                    error = "Connection test failed: ${e.message}"
                )
            }
        }
    }
}
```

### 3. Data Models (`model/ApiModels.kt`)

Define data structures for API communication and UI state.

```kotlin
package com.mac.assistant.model

import com.google.gson.annotations.SerializedName

// API Request Model
data class CommandRequest(
    @SerializedName("text")
    val text: String,
    
    @SerializedName("timestamp")
    val timestamp: Double = System.currentTimeMillis() / 1000.0,
    
    @SerializedName("metadata")
    val metadata: Map<String, Any>? = null
)

// API Response Model
data class CommandResponse(
    @SerializedName("message")
    val message: String,
    
    @SerializedName("data")
    val data: Map<String, Any>? = null,
    
    @SerializedName("status")
    val status: String,
    
    @SerializedName("timestamp")
    val timestamp: Double,
    
    @SerializedName("execution_time")
    val executionTime: Double
)

// Health Check Response
data class HealthResponse(
    @SerializedName("message")
    val message: String,
    
    @SerializedName("version")
    val version: String,
    
    @SerializedName("status")
    val status: String,
    
    @SerializedName("timestamp")
    val timestamp: String
)

// UI State Model
data class AssistantUiState(
    val isLoading: Boolean = false,
    val isListening: Boolean = false,
    val isConnected: Boolean = false,
    val isTestingConnection: Boolean = false,
    val lastCommand: String? = null,
    val lastResponse: CommandResponse? = null,
    val error: String? = null,
    val serverAddress: String = "192.168.1.100:8000",
    val commandHistory: List<Pair<String, CommandResponse>> = emptyList()
)
```

### 4. Network Layer (`network/ApiService.kt`)

Handles HTTP communication with the Windows backend.

```kotlin
package com.mac.assistant.network

import com.mac.assistant.model.CommandRequest
import com.mac.assistant.model.CommandResponse
import com.mac.assistant.model.HealthResponse
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface ApiService {
    
    @GET("/")
    suspend fun healthCheck(): HealthResponse
    
    @POST("/command")
    suspend fun executeCommand(@Body request: CommandRequest): CommandResponse
    
    @GET("/status")
    suspend fun getSystemStatus(): Map<String, Any>
}
```

### 5. Repository (`repository/AssistantRepository.kt`)

Abstracts data access and provides a clean API for the ViewModel.

```kotlin
package com.mac.assistant.repository

import com.mac.assistant.model.CommandRequest
import com.mac.assistant.model.CommandResponse
import com.mac.assistant.network.ApiService
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AssistantRepository @Inject constructor(
    private val apiService: ApiService
) {
    
    suspend fun executeCommand(text: String): CommandResponse = withContext(Dispatchers.IO) {
        val request = CommandRequest(
            text = text,
            timestamp = System.currentTimeMillis() / 1000.0,
            metadata = mapOf(
                "source" to "android_app",
                "app_version" to "1.0.0"
            )
        )
        
        return@withContext apiService.executeCommand(request)
    }
    
    suspend fun testConnection(): Boolean = withContext(Dispatchers.IO) {
        return@withContext try {
            val response = apiService.healthCheck()
            response.status == "healthy"
        } catch (e: Exception) {
            false
        }
    }
    
    suspend fun getSystemStatus(): Map<String, Any> = withContext(Dispatchers.IO) {
        return@withContext apiService.getSystemStatus()
    }
    
    fun updateServerAddress(address: String) {
        // Update server address in network configuration
        // This would typically involve recreating the Retrofit instance
    }
}
```

### 6. Voice Manager (`service/VoiceManager.kt`)

Handles voice input recording and processing.

```kotlin
package com.mac.assistant.service

import android.content.Context
import android.media.MediaRecorder
import android.os.Build
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.io.File
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class VoiceManager @Inject constructor(
    private val context: Context
) {
    
    private var mediaRecorder: MediaRecorder? = null
    private var recordingFile: File? = null
    
    private val _isRecording = MutableStateFlow(false)
    val isRecording: StateFlow<Boolean> = _isRecording.asStateFlow()
    
    private val _audioLevel = MutableStateFlow(0f)
    val audioLevel: StateFlow<Float> = _audioLevel.asStateFlow()
    
    fun startRecording(): Boolean {
        try {
            // Create temporary file for recording
            recordingFile = File.createTempFile("voice_", ".3gp", context.cacheDir)
            
            // Initialize MediaRecorder
            mediaRecorder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                MediaRecorder(context)
            } else {
                @Suppress("DEPRECATION")
                MediaRecorder()
            }
            
            mediaRecorder?.apply {
                setAudioSource(MediaRecorder.AudioSource.MIC)
                setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP)
                setAudioEncoder(MediaRecorder.AudioEncoder.AMR_NB)
                setOutputFile(recordingFile?.absolutePath)
                
                prepare()
                start()
            }
            
            _isRecording.value = true
            return true
            
        } catch (e: Exception) {
            e.printStackTrace()
            return false
        }
    }
    
    fun stopRecording(): File? {
        return try {
            mediaRecorder?.apply {
                stop()
                release()
            }
            mediaRecorder = null
            
            _isRecording.value = false
            
            recordingFile
            
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
    
    fun getMaxAmplitude(): Int {
        return mediaRecorder?.maxAmplitude ?: 0
    }
}
```

## User Interface

### Main Screen (`ui/screens/MainScreen.kt`)

The primary interface for user interaction.

```kotlin
package com.mac.assistant.ui.screens

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.mac.assistant.ui.components.ResponseCard
import com.mac.assistant.ui.components.StatusIndicator
import com.mac.assistant.ui.components.VoiceButton
import com.mac.assistant.viewmodel.AssistantViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(viewModel: AssistantViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Top App Bar
        TopAppBar(
            title = { Text("MAC Assistant") },
            actions = {
                IconButton(onClick = { /* Open settings */ }) {
                    Icon(Icons.Default.Settings, contentDescription = "Settings")
                }
            }
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Connection Status
        StatusIndicator(
            isConnected = uiState.isConnected,
            serverAddress = uiState.serverAddress,
            onTestConnection = { viewModel.testConnection() }
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Voice Input Button
        VoiceButton(
            isListening = uiState.isListening,
            isLoading = uiState.isLoading,
            onClick = { /* Handle voice input */ }
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Last Response
        uiState.lastResponse?.let { response ->
            ResponseCard(
                command = uiState.lastCommand ?: "",
                response = response,
                modifier = Modifier.fillMaxWidth()
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Command History
        if (uiState.commandHistory.isNotEmpty()) {
            Text(
                text = "Command History",
                style = MaterialTheme.typography.headlineSmall,
                modifier = Modifier.padding(bottom = 8.dp)
            )
            
            LazyColumn {
                items(uiState.commandHistory.reversed()) { (command, response) ->
                    ResponseCard(
                        command = command,
                        response = response,
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp)
                    )
                }
            }
        }
        
        // Error Display
        uiState.error?.let { error ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.errorContainer
                )
            ) {
                Text(
                    text = error,
                    modifier = Modifier.padding(16.dp),
                    color = MaterialTheme.colorScheme.onErrorContainer
                )
            }
        }
    }
}
```

### Voice Button Component (`ui/components/VoiceButton.kt`)

Animated button for voice input.

```kotlin
package com.mac.assistant.ui.components

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.unit.dp

@Composable
fun VoiceButton(
    isListening: Boolean,
    isLoading: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val scale by animateFloatAsState(
        targetValue = if (isListening) 1.2f else 1.0f,
        label = "Voice button scale"
    )
    
    FloatingActionButton(
        onClick = onClick,
        modifier = modifier
            .size(80.dp)
            .scale(scale),
        containerColor = if (isListening) {
            MaterialTheme.colorScheme.error
        } else {
            MaterialTheme.colorScheme.primary
        }
    ) {
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(24.dp),
                color = MaterialTheme.colorScheme.onPrimary
            )
        } else {
            Icon(
                Icons.Default.Mic,
                contentDescription = if (isListening) "Stop listening" else "Start listening",
                modifier = Modifier.size(32.dp)
            )
        }
    }
}
```

## Setup and Building

### Development Environment

1. **Install Android Studio**
   - Download from [developer.android.com](https://developer.android.com/studio)
   - Install Android SDK (API level 26+)
   - Set up emulator or connect physical device

2. **Open Project**
   ```bash
   # Navigate to Android project
   cd android/MACAssistant
   
   # Open in Android Studio
   studio .
   ```

3. **Sync and Build**
   - Android Studio will prompt to sync Gradle files
   - Wait for sync to complete
   - Build project with Ctrl+F9

### Dependencies (`app/build.gradle.kts`)

```kotlin
dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.activity:activity-compose:1.8.2")
    
    // Compose BOM
    implementation(platform("androidx.compose:compose-bom:2023.10.01"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    
    // ViewModel
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
    
    // Hilt for Dependency Injection
    implementation("com.google.dagger:hilt-android:2.48")
    kapt("com.google.dagger:hilt-compiler:2.48")
    
    // Retrofit for API calls
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
    // Testing
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation(platform("androidx.compose:compose-bom:2023.10.01"))
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
}
```

### Building APK

```bash
# Debug build
./gradlew assembleDebug

# Release build
./gradlew assembleRelease

# Install on connected device
./gradlew installDebug
```

## Features and Functionality

### Voice Input

**Features:**
- Touch-to-talk voice recording
- Visual feedback during recording
- Audio level monitoring
- Background noise suppression

**Implementation:**
- Uses Android MediaRecorder API
- Records in 3GP format for compatibility
- Provides real-time audio level feedback
- Handles permissions automatically

### Network Communication

**Features:**
- HTTP API communication with Windows backend
- Connection status monitoring
- Retry logic for failed requests
- Error handling and user feedback

**Security:**
- Local network communication only
- No external internet dependencies
- Request/response validation
- Timeout handling

### User Interface

**Material Design 3:**
- Dynamic color theming
- Responsive layout design
- Accessibility support
- Dark/light theme support

**Key UI Elements:**
- Animated voice input button
- Real-time connection status
- Command history display
- Error handling with user feedback

## Testing

### Unit Tests

```kotlin
@Test
fun `executeCommand should update UI state correctly`() = runTest {
    // Given
    val repository = mockk<AssistantRepository>()
    val expectedResponse = CommandResponse(
        message = "Test response",
        data = null,
        status = "success",
        timestamp = 123456789.0,
        executionTime = 50.0
    )
    
    coEvery { repository.executeCommand(any()) } returns expectedResponse
    
    val viewModel = AssistantViewModel(repository)
    
    // When
    viewModel.executeCommand("test command")
    
    // Then
    val uiState = viewModel.uiState.value
    assertEquals("test command", uiState.lastCommand)
    assertEquals(expectedResponse, uiState.lastResponse)
    assertFalse(uiState.isLoading)
}
```

### Integration Tests

```kotlin
@Test
fun `app should communicate with server successfully`() {
    // Test actual network communication
    // Requires running server for integration testing
}
```

## Troubleshooting

### Common Issues

1. **App crashes on startup**
   - Check Android version compatibility
   - Verify all dependencies are properly installed
   - Check for permission issues

2. **Can't connect to server**
   - Verify server is running on Windows
   - Check IP address and port configuration
   - Ensure devices are on same network

3. **Voice recording not working**
   - Check microphone permissions
   - Verify device has microphone
   - Test with other voice recording apps

### Debug Tips

```kotlin
// Enable network logging
if (BuildConfig.DEBUG) {
    val loggingInterceptor = HttpLoggingInterceptor()
    loggingInterceptor.level = HttpLoggingInterceptor.Level.BODY
    
    OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .build()
}
```

This Android app documentation provides comprehensive information for development, deployment, and troubleshooting of the MAC Assistant mobile interface.
