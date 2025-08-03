package com.mac.assistant.network

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import com.mac.assistant.model.CommandRequest
import com.mac.assistant.model.CommandResponse
import com.mac.assistant.model.HealthResponse

interface ApiService {
    
    @GET("health")
    suspend fun getHealth(): Response<HealthResponse>
    
    @POST("command")
    suspend fun sendCommand(@Body request: CommandRequest): Response<CommandResponse>
    
    @GET("info")
    suspend fun getSystemInfo(): Response<Map<String, Any>>
    
    @GET("commands")
    suspend fun getAvailableCommands(): Response<Map<String, Any>>
}
