package com.mac.assistant.model

data class CommandRequest(
    val text: String,
    val client_id: String? = null,
    val timestamp: Double? = null
)

data class CommandResponse(
    val status: String,
    val message: String,
    val data: Map<String, Any>? = null,
    val processing_time: Double,
    val server_timestamp: Double
)

data class HealthResponse(
    val status: String,
    val message: String,
    val platform: String,
    val uptime: Double,
    val version: String
)
