package com.mac.assistant.repository

import com.mac.assistant.network.ApiClient
import com.mac.assistant.model.CommandRequest
import com.mac.assistant.model.CommandResponse
import com.mac.assistant.model.HealthResponse
import retrofit2.Response
import java.util.UUID

class AssistantRepository {
    
    private val clientId = UUID.randomUUID().toString()
    
    suspend fun testConnection(serverUrl: String): Response<HealthResponse> {
        val formattedUrl = ApiClient.formatUrl(serverUrl)
        val apiService = ApiClient.getClient(formattedUrl)
        return apiService.getHealth()
    }
    
    suspend fun sendCommand(serverUrl: String, command: String): CommandResponse {
        val formattedUrl = ApiClient.formatUrl(serverUrl)
        val apiService = ApiClient.getClient(formattedUrl)
        
        val request = CommandRequest(
            text = command,
            client_id = clientId,
            timestamp = System.currentTimeMillis().toDouble() / 1000.0
        )
        
        val response = apiService.sendCommand(request)
        
        if (response.isSuccessful) {
            return response.body() ?: CommandResponse(
                status = "error",
                message = "Empty response from server",
                processing_time = 0.0,
                server_timestamp = System.currentTimeMillis().toDouble() / 1000.0
            )
        } else {
            throw Exception("HTTP ${response.code()}: ${response.message()}")
        }
    }
    
    suspend fun getSystemInfo(serverUrl: String): Map<String, Any>? {
        val formattedUrl = ApiClient.formatUrl(serverUrl)
        val apiService = ApiClient.getClient(formattedUrl)
        
        val response = apiService.getSystemInfo()
        return if (response.isSuccessful) {
            response.body()
        } else {
            null
        }
    }
    
    suspend fun getAvailableCommands(serverUrl: String): Map<String, Any>? {
        val formattedUrl = ApiClient.formatUrl(serverUrl)
        val apiService = ApiClient.getClient(formattedUrl)
        
        val response = apiService.getAvailableCommands()
        return if (response.isSuccessful) {
            response.body()
        } else {
            null
        }
    }
}
