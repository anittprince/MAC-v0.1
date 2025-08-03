"""
MAC Assistant - FastAPI Server
HTTP API server for receiving text commands and returning responses.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import logging
import time
from core.brain import MACBrain

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app instance
app = FastAPI(
    title="MAC Assistant API",
    description="Cross-platform voice assistant HTTP API",
    version="1.0.0"
)

# Enable CORS for cross-origin requests (important for Android app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the brain
brain = MACBrain()

# Request/Response models
class CommandRequest(BaseModel):
    text: str
    client_id: Optional[str] = None
    timestamp: Optional[float] = None

class CommandResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    processing_time: float
    server_timestamp: float

class HealthResponse(BaseModel):
    status: str
    message: str
    platform: str
    uptime: float
    version: str

# Server start time for uptime calculation
server_start_time = time.time()

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic information."""
    return {
        "name": "MAC Assistant API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "command": "/command",
            "info": "/info"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    uptime = time.time() - server_start_time
    platform_info = brain.get_platform_info()
    
    return HealthResponse(
        status="healthy",
        message="MAC Assistant API is running",
        platform=platform_info.get('platform', 'unknown'),
        uptime=uptime,
        version="1.0.0"
    )

@app.post("/command", response_model=CommandResponse)
async def process_command(request: CommandRequest, http_request: Request):
    """Process a text command and return response."""
    start_time = time.time()
    
    try:
        # Log the incoming request
        client_ip = http_request.client.host
        logger.info(f"Command received from {client_ip}: {request.text}")
        
        # Validate input
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Empty command text")
        
        # Process the command using the brain
        result = brain.process_command(request.text.strip())
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log the result
        logger.info(f"Command processed in {processing_time:.3f}s: {result['status']}")
        
        return CommandResponse(
            status=result['status'],
            message=result['message'],
            data=result.get('data'),
            processing_time=processing_time,
            server_timestamp=time.time()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error processing command: {str(e)}")
        
        return CommandResponse(
            status="error",
            message=f"Internal server error: {str(e)}",
            data=None,
            processing_time=processing_time,
            server_timestamp=time.time()
        )

@app.get("/info", response_model=Dict[str, Any])
async def get_system_info():
    """Get system and platform information."""
    try:
        platform_info = brain.get_platform_info()
        available_commands = brain.get_available_commands()
        
        return {
            "platform": platform_info,
            "available_commands": list(available_commands.keys()),
            "command_patterns": available_commands,
            "server_info": {
                "uptime": time.time() - server_start_time,
                "version": "1.0.0"
            }
        }
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/commands", response_model=Dict[str, Any])
async def get_available_commands():
    """Get list of available command patterns."""
    try:
        commands = brain.get_available_commands()
        return {
            "commands": commands,
            "total_patterns": sum(len(patterns) for patterns in commands.values()),
            "categories": list(commands.keys())
        }
    except Exception as e:
        logger.error(f"Error getting commands: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return {
        "status": "error",
        "message": f"Endpoint not found: {request.url.path}",
        "available_endpoints": ["/", "/health", "/command", "/info", "/commands"]
    }

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {str(exc)}")
    return {
        "status": "error",
        "message": "Internal server error",
        "detail": str(exc)
    }

def run_server(host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
    """Run the FastAPI server."""
    logger.info(f"Starting MAC Assistant API server on {host}:{port}")
    logger.info(f"Platform: {brain.get_platform_info().get('platform', 'unknown')}")
    
    uvicorn.run(
        "sync.api:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MAC Assistant API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    run_server(host=args.host, port=args.port, debug=args.debug)
