# API Documentation

This document provides comprehensive documentation for the MAC Assistant HTTP API, which enables communication between the Android app and Windows backend.

## Overview

The MAC Assistant API is a RESTful HTTP API built with FastAPI that allows cross-platform communication. The API runs on the Windows machine and accepts commands from the Android app over the local network.

**Base URL:** `http://<windows-ip>:8000`

**Content Type:** `application/json`

**Communication Pattern:** Request-Response (synchronous)

## API Endpoints

### 1. Health Check

Check if the API server is running and responsive.

**Endpoint:** `GET /`

**Description:** Returns basic server status and information.

**Request:**
```http
GET / HTTP/1.1
Host: 192.168.1.100:8000
```

**Response:**
```json
{
  "message": "MAC Assistant API is running",
  "version": "1.0.0",
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response Codes:**
- `200 OK` - Server is running normally
- `500 Internal Server Error` - Server error

### 2. Execute Command

Process a voice command and return the result.

**Endpoint:** `POST /command`

**Description:** Executes a voice command and returns the processed result.

**Request Model:**
```json
{
  "text": "string (required, 1-1000 characters)",
  "timestamp": "number (optional, Unix timestamp)",
  "metadata": "object (optional, additional context)"
}
```

**Request Example:**
```http
POST /command HTTP/1.1
Host: 192.168.1.100:8000
Content-Type: application/json

{
  "text": "what time is it",
  "timestamp": 1642248600.0,
  "metadata": {
    "source": "android_app",
    "user_id": "user123"
  }
}
```

**Response Model:**
```json
{
  "message": "string (human-readable response)",
  "data": "object (structured command result)",
  "status": "string (success|error)",
  "timestamp": "number (Unix timestamp)",
  "execution_time": "number (milliseconds)"
}
```

**Success Response Example:**
```json
{
  "message": "The current time is 02:30 PM on Monday, January 15, 2024",
  "data": {
    "time": "02:30 PM",
    "date": "Monday, January 15, 2024",
    "timestamp": 1642248600.0
  },
  "status": "success",
  "timestamp": 1642248600.123,
  "execution_time": 45
}
```

**Error Response Example:**
```json
{
  "message": "I didn't understand that command. Please try again.",
  "data": null,
  "status": "error",
  "timestamp": 1642248600.123,
  "execution_time": 12
}
```

**Response Codes:**
- `200 OK` - Command processed successfully
- `400 Bad Request` - Invalid request format
- `422 Unprocessable Entity` - Request validation failed
- `500 Internal Server Error` - Server error during processing

### 3. System Status

Get detailed system information and API status.

**Endpoint:** `GET /status`

**Description:** Returns comprehensive system and API status information.

**Request:**
```http
GET /status HTTP/1.1
Host: 192.168.1.100:8000
```

**Response:**
```json
{
  "api_status": "running",
  "system_info": {
    "os": "Windows",
    "version": "10.0.19044",
    "hostname": "DESKTOP-ABC123",
    "cpu_usage": "15.2%",
    "memory_usage": "68.4%",
    "disk_usage": "45.2%"
  },
  "voice_engine": {
    "input_available": true,
    "output_available": true,
    "model_loaded": true
  },
  "network": {
    "ip_address": "192.168.1.100",
    "port": 8000,
    "active_connections": 2
  },
  "timestamp": 1642248600.0
}
```

**Response Codes:**
- `200 OK` - Status retrieved successfully
- `500 Internal Server Error` - Unable to retrieve status

## Data Models

### CommandRequest

Input model for command execution.

```python
class CommandRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Command text")
    timestamp: Optional[float] = Field(None, description="Unix timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional context")
```

**Validation Rules:**
- `text`: Required, 1-1000 characters
- `timestamp`: Optional, valid Unix timestamp
- `metadata`: Optional, arbitrary JSON object

### CommandResponse

Output model for command results.

```python
class CommandResponse(BaseModel):
    message: str = Field(..., description="Human-readable response")
    data: Optional[Dict[str, Any]] = Field(None, description="Structured result data")
    status: str = Field(..., description="Response status")
    timestamp: float = Field(..., description="Response timestamp")
    execution_time: float = Field(..., description="Execution time in milliseconds")
```

## Command Categories and Examples

### 1. Greeting Commands

**Input:** `"hello MAC"`, `"hi there"`, `"good morning"`

**Response:**
```json
{
  "message": "Good afternoon, User! I'm MAC, your voice assistant. How can I help you today?",
  "data": {
    "greeting": "Good afternoon",
    "time": "14:30:15",
    "user": "User"
  },
  "status": "success"
}
```

### 2. Time and Date Commands

**Input:** `"what time is it"`, `"current time"`, `"what's the date"`

**Response:**
```json
{
  "message": "The current time is 02:30 PM on Monday, January 15, 2024",
  "data": {
    "time": "02:30 PM",
    "date": "Monday, January 15, 2024",
    "timestamp": 1642248600.0
  },
  "status": "success"
}
```

### 3. System Information Commands

**Input:** `"system info"`, `"computer status"`, `"how's my pc"`

**Response:**
```json
{
  "message": "System Status: CPU 15%, RAM 68%, Disk 45%",
  "data": {
    "cpu_usage": "15.2%",
    "memory_usage": "68.4%",
    "memory_available": "2.8 GB",
    "disk_usage": "45.2%",
    "disk_free": "125.3 GB",
    "os": "Windows",
    "hostname": "DESKTOP-ABC123"
  },
  "status": "success"
}
```

### 4. Volume Control Commands

**Input:** `"volume up"`, `"turn down sound"`, `"mute"`, `"unmute"`

**Response:**
```json
{
  "message": "Volume increased to 75%",
  "data": {
    "volume": 75,
    "action": "increased",
    "is_muted": false
  },
  "status": "success"
}
```

### 5. Application Commands

**Input:** `"open calculator"`, `"launch notepad"`, `"start browser"`

**Response:**
```json
{
  "message": "Opening calc.exe",
  "data": {
    "application": "calc.exe",
    "action": "opened"
  },
  "status": "success"
}
```

### 6. Network Commands

**Input:** `"network status"`, `"check connection"`, `"show ip"`

**Response:**
```json
{
  "message": "Network Status: Connected. Found 3 active interfaces.",
  "data": {
    "internet_status": "Connected",
    "interfaces": [
      {
        "name": "Wi-Fi",
        "ip": "192.168.1.100",
        "status": "up"
      }
    ]
  },
  "status": "success"
}
```

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "message": "Error description for user",
  "data": null,
  "status": "error",
  "timestamp": 1642248600.123,
  "execution_time": 12,
  "error_code": "COMMAND_NOT_RECOGNIZED",
  "details": "Additional technical details"
}
```

### Common Error Codes

| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| `COMMAND_NOT_RECOGNIZED` | Command pattern not matched | 200 |
| `INVALID_REQUEST` | Request format invalid | 400 |
| `VALIDATION_ERROR` | Request validation failed | 422 |
| `SYSTEM_ERROR` | Internal system error | 500 |
| `PERMISSION_DENIED` | Insufficient permissions | 403 |
| `SERVICE_UNAVAILABLE` | Required service unavailable | 503 |

### Error Examples

**Unrecognized Command:**
```json
{
  "message": "I didn't understand that command. Please try again.",
  "data": null,
  "status": "error",
  "error_code": "COMMAND_NOT_RECOGNIZED"
}
```

**Permission Error:**
```json
{
  "message": "System power commands are disabled for safety.",
  "data": null,
  "status": "error",
  "error_code": "PERMISSION_DENIED"
}
```

**System Error:**
```json
{
  "message": "Error getting system information: Access denied",
  "data": null,
  "status": "error",
  "error_code": "SYSTEM_ERROR"
}
```

## Authentication and Security

### Current Security Model

**Local Network Only:**
- API server binds to local network interfaces only
- No external internet access required
- CORS enabled for local network origins

**Input Validation:**
- All inputs validated using Pydantic models
- Text length limits enforced
- Special character filtering

**Safe Operations:**
- System shutdown/restart commands disabled
- File operations limited to safe directories
- Application closing requires confirmation

### Future Security Enhancements

**Authentication (Planned):**
```http
Authorization: Bearer <jwt_token>
```

**Rate Limiting (Planned):**
- Maximum requests per minute per client
- Command execution throttling

**Encryption (Planned):**
- HTTPS support with self-signed certificates
- Request/response encryption

## Rate Limiting and Performance

### Current Limits

- **Request Size:** Maximum 1MB
- **Text Length:** Maximum 1000 characters
- **Concurrent Connections:** 10 simultaneous
- **Timeout:** 30 seconds per request

### Performance Optimizations

**Caching:**
- System information cached for 30 seconds
- Network status cached for 10 seconds
- Application list cached for 60 seconds

**Async Processing:**
- Non-blocking request handling
- Background command execution
- Connection pooling

## CORS Configuration

**Allowed Origins:**
```python
origins = [
    "http://localhost:*",
    "http://192.168.*.*:*",
    "http://10.*.*.*:*",
    "http://172.16.*.*:*"
]
```

**Allowed Methods:**
- `GET`
- `POST`
- `OPTIONS`

**Allowed Headers:**
- `Content-Type`
- `Authorization`
- `X-Requested-With`

## Client Implementation Examples

### Android Kotlin

```kotlin
class ApiService {
    private val retrofit = Retrofit.Builder()
        .baseUrl("http://192.168.1.100:8000/")
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    private val api = retrofit.create(MacApi::class.java)
    
    suspend fun executeCommand(text: String): CommandResponse {
        val request = CommandRequest(
            text = text,
            timestamp = System.currentTimeMillis() / 1000.0
        )
        return api.executeCommand(request)
    }
}
```

### JavaScript/Web

```javascript
class MacApiClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }
    
    async executeCommand(text) {
        const response = await fetch(`${this.baseUrl}/command`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                timestamp: Date.now() / 1000
            })
        });
        
        return await response.json();
    }
}
```

### Python Client

```python
import requests

class MacApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def execute_command(self, text):
        response = requests.post(
            f"{self.base_url}/command",
            json={
                "text": text,
                "timestamp": time.time()
            }
        )
        return response.json()
```

## Testing and Development

### API Testing

**Using curl:**
```bash
# Health check
curl http://192.168.1.100:8000/

# Execute command
curl -X POST http://192.168.1.100:8000/command \
  -H "Content-Type: application/json" \
  -d '{"text": "what time is it"}'

# Get status
curl http://192.168.1.100:8000/status
```

**Using HTTPie:**
```bash
# Execute command
http POST 192.168.1.100:8000/command text="volume up"

# Get status
http GET 192.168.1.100:8000/status
```

### Interactive API Documentation

**Swagger UI:** Visit `http://192.168.1.100:8000/docs` for interactive API documentation.

**ReDoc:** Visit `http://192.168.1.100:8000/redoc` for alternative documentation format.

### Development Server

Start development server with auto-reload:
```bash
uvicorn sync.api:app --host 0.0.0.0 --port 8000 --reload
```

## Monitoring and Logging

### Request Logging

All API requests are logged with:
- Timestamp
- Client IP address
- Request method and path
- Response status code
- Execution time

### Performance Metrics

Available at `/status` endpoint:
- Average response time
- Request count per hour
- Error rate
- Memory usage
- CPU usage

### Health Monitoring

Monitor API health by checking:
- `/` endpoint response time
- `/status` endpoint data
- Error rates in logs
- System resource usage

This API documentation provides the foundation for building clients and integrating with the MAC Assistant system.
