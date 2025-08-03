"""
MAC Assistant - Main Entry Point
Integrates voice input, brain processing, and voice output.
"""

import sys
import time
import threading
import argparse
from typing import Optional

# Import core modules
from core.brain import MACBrain
from core.voice_input import VoiceInput
from core.voice_output import VoiceOutput

class MACAssistant:
    def __init__(self, model_path: str = "models/vosk-model"):
        """Initialize the MAC Assistant."""
        print("Initializing MAC Assistant...")
        
        # Initialize components
        self.brain = MACBrain()
        self.voice_output = VoiceOutput()
        self.voice_input = None
        self.is_running = False
        
        # Show AI services status
        self._show_ai_status()
        
        # Try to initialize voice input
        try:
            self.voice_input = VoiceInput(model_path)
            print("Voice input initialized successfully")
        except Exception as e:
            print(f"Warning: Voice input initialization failed: {e}")
            print("Voice commands will not be available")
        
        print("MAC Assistant initialized successfully")
    
    def start_voice_mode(self):
        """Start the voice interaction mode."""
        if not self.voice_input:
            print("Voice input is not available. Please check your microphone and Vosk model.")
            return
        
        if not self.voice_input.is_microphone_available():
            print("Microphone is not available. Please check your audio setup.")
            return
        
        print("\n" + "="*50)
        print("MAC Assistant - Voice Mode")
        print("="*50)
        print("Say 'hello' to start or 'quit' to exit")
        print("Listening for voice commands...")
        
        self.is_running = True
        self.voice_output.speak("Hello! I'm MAC, your voice assistant. How can I help you?")
        
        try:
            while self.is_running:
                # Listen for voice command
                command_text = self.voice_input.listen_once(timeout=10.0)
                
                if command_text:
                    print(f"\nYou said: {command_text}")
                    
                    # Check for exit commands
                    if any(word in command_text.lower() for word in ['quit', 'exit', 'goodbye', 'bye']):
                        self.voice_output.speak("Goodbye! Have a great day!")
                        self.is_running = False
                        break
                    
                    # Process the command
                    self._process_voice_command(command_text)
                else:
                    # No command received, continue listening
                    continue
                    
        except KeyboardInterrupt:
            print("\nReceived interrupt signal")
            self.voice_output.speak("Goodbye!")
            self.is_running = False
        except Exception as e:
            print(f"Error in voice mode: {e}")
            self.voice_output.speak("I encountered an error and need to stop.")
            self.is_running = False
    
    def start_text_mode(self):
        """Start the text interaction mode."""
        print("\n" + "="*50)
        print("MAC Assistant - Text Mode")
        print("="*50)
        print("Type your commands or 'quit' to exit")
        
        self.is_running = True
        
        try:
            while self.is_running:
                # Get text input
                try:
                    command_text = input("\nMAC> ").strip()
                except EOFError:
                    break
                
                if not command_text:
                    continue
                
                # Check for exit commands
                if command_text.lower() in ['quit', 'exit', 'goodbye', 'bye']:
                    print("Goodbye! Have a great day!")
                    self.is_running = False
                    break
                
                # Process the command
                self._process_text_command(command_text)
                
        except KeyboardInterrupt:
            print("\nReceived interrupt signal")
            self.is_running = False
    
    def _process_voice_command(self, command_text: str):
        """Process a voice command and speak the response."""
        try:
            # Process command through brain
            result = self.brain.process_command(command_text)
            
            # Speak the response
            response_text = result.get('message', 'I could not process that command')
            print(f"MAC: {response_text}")
            self.voice_output.speak(response_text)
            
            # Print additional data if available
            if result.get('data'):
                print(f"Additional info: {result['data']}")
            
        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            print(f"MAC: {error_msg}")
            self.voice_output.speak("I encountered an error processing your command.")
    
    def _process_text_command(self, command_text: str):
        """Process a text command and print the response."""
        try:
            # Process command through brain
            result = self.brain.process_command(command_text)
            
            # Print the response
            response_text = result.get('message', 'I could not process that command')
            print(f"MAC: {response_text}")
            
            # Print additional data if available
            if result.get('data'):
                print(f"Additional info: {result['data']}")
            
        except Exception as e:
            print(f"MAC: Error processing command: {str(e)}")
    
    def process_single_command(self, command_text: str) -> dict:
        """Process a single command and return the result."""
        return self.brain.process_command(command_text)
    
    def get_system_info(self) -> dict:
        """Get system information."""
        return self.brain.get_platform_info()
    
    def get_available_commands(self) -> dict:
        """Get available commands."""
        return self.brain.get_available_commands()
    
    def stop(self):
        """Stop the assistant."""
        self.is_running = False
        if self.voice_input:
            self.voice_input.stop_continuous_listening()
        if self.voice_output:
            self.voice_output.stop_speaking()
    
    def _show_ai_status(self):
        """Show the status of AI services."""
        try:
            ai_status = self.brain.get_ai_status()
            print("\nAI Services Status:")
            print("-" * 30)
            
            status_icons = {True: "✓", False: "✗"}
            
            print(f"{status_icons[ai_status['chatgpt']]} ChatGPT: {'Available' if ai_status['chatgpt'] else 'Not configured'}")
            print(f"{status_icons[ai_status['google_search']]} Google Search: {'Available' if ai_status['google_search'] else 'Using fallback'}")
            print(f"{status_icons[ai_status['youtube_search']]} YouTube Search: {'Available' if ai_status['youtube_search'] else 'Not available'}")
            print(f"{status_icons[ai_status['weather']]} Weather: {'Available' if ai_status['weather'] else 'Not configured'}")
            
            if not any(ai_status.values()):
                print("\n💡 To enable AI features, copy .env.template to .env and add your API keys")
            else:
                print("\n🤖 AI features are ready! Try asking general questions.")
            
            print()
            
        except Exception as e:
            print(f"Could not check AI status: {e}")


def print_banner():
    """Print the MAC Assistant banner."""
    banner = """
╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║    ███    ███  █████   ██████     █████  ███████ ███████ ██ ███████ ████████   ║
║    ████  ████ ██   ██ ██        ██   ██ ██      ██      ██ ██         ██      ║
║    ██ ████ ██ ███████ ██        ███████ ███████ ███████ ██ ███████    ██      ║
║    ██  ██  ██ ██   ██ ██        ██   ██      ██      ██ ██      ██    ██      ║
║    ██      ██ ██   ██  ██████   ██   ██ ███████ ███████ ██ ███████    ██      ║
║                                                                                ║
║                        Cross-Platform Voice Assistant                         ║
║                                  v1.0.0                                       ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="MAC Assistant - Cross-Platform Voice Assistant")
    parser.add_argument("--mode", choices=["voice", "text", "server"], default="voice",
                       help="Mode to run in: voice (default), text, or server")
    parser.add_argument("--model", default="models/vosk-model",
                       help="Path to Vosk model directory")
    parser.add_argument("--host", default="0.0.0.0", help="Server host (server mode only)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (server mode only)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    if args.mode == "server":
        # Run as API server
        print("Starting MAC Assistant API Server...")
        from sync.api import run_server
        run_server(host=args.host, port=args.port, debug=args.debug)
    
    elif args.mode == "text":
        # Run in text mode
        assistant = MACAssistant(model_path=args.model)
        assistant.start_text_mode()
    
    elif args.mode == "voice":
        # Run in voice mode (default)
        assistant = MACAssistant(model_path=args.model)
        assistant.start_voice_mode()
    
    else:
        print(f"Unknown mode: {args.mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
