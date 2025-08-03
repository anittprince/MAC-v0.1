package com.mac.assistant.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import com.mac.assistant.repository.AssistantRepository
import com.mac.assistant.model.CommandResponse

data class AssistantUiState(
    val isListening: Boolean = false,
    val isConnected: Boolean = false,
    val serverUrl: String = "",
    val lastCommand: String = "",
    val lastResponse: String = "",
    val hasAudioPermission: Boolean = false,
    val isLoading: Boolean = false,
    val error: String? = null
)

class AssistantViewModel : ViewModel() {
    
    private val repository = AssistantRepository()
    
    private val _uiState = MutableStateFlow(AssistantUiState())
    val uiState: StateFlow<AssistantUiState> = _uiState.asStateFlow()
    
    fun onPermissionGranted() {
        _uiState.value = _uiState.value.copy(hasAudioPermission = true)
    }
    
    fun onPermissionDenied() {
        _uiState.value = _uiState.value.copy(
            hasAudioPermission = false,
            error = "Audio permission is required for voice commands"
        )
    }
    
    fun updateServerUrl(url: String) {
        _uiState.value = _uiState.value.copy(serverUrl = url, error = null)
    }
    
    fun testConnection() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            
            try {
                val response = repository.testConnection(_uiState.value.serverUrl)
                _uiState.value = _uiState.value.copy(
                    isConnected = response.isSuccessful,
                    isLoading = false,
                    error = if (response.isSuccessful) null else "Connection failed"
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isConnected = false,
                    isLoading = false,
                    error = "Connection error: ${e.message}"
                )
            }
        }
    }
    
    fun sendCommand(command: String) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                isLoading = true,
                lastCommand = command,
                error = null
            )
            
            try {
                val response = repository.sendCommand(_uiState.value.serverUrl, command)
                _uiState.value = _uiState.value.copy(
                    lastResponse = response.message,
                    isLoading = false,
                    error = if (response.status == "error") response.message else null
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    lastResponse = "",
                    isLoading = false,
                    error = "Command error: ${e.message}"
                )
            }
        }
    }
    
    fun startListening() {
        _uiState.value = _uiState.value.copy(isListening = true, error = null)
    }
    
    fun stopListening() {
        _uiState.value = _uiState.value.copy(isListening = false)
    }
    
    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
    
    fun onVoiceResult(result: String) {
        stopListening()
        if (result.isNotBlank()) {
            sendCommand(result)
        }
    }
    
    fun onVoiceError(error: String) {
        _uiState.value = _uiState.value.copy(
            isListening = false,
            error = "Voice recognition error: $error"
        )
    }
}
