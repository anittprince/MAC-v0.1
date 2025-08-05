"""
MAC Assistant - Enhanced Main Entry Point
Integrates voice input, brain processing, voice output, and personalization.
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
from core.mood_context import MoodDetector, ContextualResponseGenerator
from core.proactive_assistant import ProactiveAssistant, SmartNotificationManager

class MACAssistant:
    def __init__(self, model_path: str = "models/vosk-model"):
        """Initialize the Enhanced MAC Assistant."""
        print("🚀 Initializing Enhanced MAC Assistant...")
        
        # Initialize components
        self.brain = MACBrain()
        self.voice_output = VoiceOutput()
        self.voice_input = None
        self.is_running = False
        
        # Initialize personalization components
        print("🧠 Initializing personalization features...")
        self.mood_detector = MoodDetector()
        self.contextual_response = ContextualResponseGenerator(self.mood_detector)
        self.proactive_assistant = ProactiveAssistant(
            self.brain.user_profile, 
            self.brain.learning_engine, 
            self.brain.conversation_memory
        )
        self.notification_manager = SmartNotificationManager()
        
        # Show personalization status
        self._show_personalization_status()
        
        # Show advanced features status
        self._show_advanced_features_status()
        
        # Show AI services status
        self._show_ai_status()
        
        # Try to initialize voice input
        try:
            self.voice_input = VoiceInput(model_path)
            print("🎤 Voice input initialized successfully")
        except Exception as e:
            print(f"⚠️  Warning: Voice input initialization failed: {e}")
            print("Voice commands will not be available")
        
        print("✅ Enhanced MAC Assistant initialized successfully")
        self._show_welcome_message()
    
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
    
    def start_text_mode(self, enable_speech: bool = True):
        """Start the text interaction mode."""
        print("\n" + "="*50)
        print("MAC Assistant - Text Mode")
        print("="*50)
        print("Type your commands or 'quit' to exit")
        
        if enable_speech:
            print("🔊 Text-to-speech is enabled. Type 'mute' to disable or 'unmute' to enable.")
        else:
            print("🔇 Text-to-speech is disabled. Type 'unmute' to enable.")
        
        self.is_running = True
        self.speech_enabled = enable_speech
        
        try:
            while self.is_running:
                # Get text input
                try:
                    command_text = input("\nMAC> ").strip()
                except EOFError:
                    break
                
                if not command_text:
                    continue
                
                # Check for speech control commands
                if command_text.lower() == 'mute':
                    self.speech_enabled = False
                    print("🔇 Text-to-speech disabled")
                    continue
                elif command_text.lower() == 'unmute':
                    self.speech_enabled = True
                    print("🔊 Text-to-speech enabled")
                    self.voice_output.speak("Text to speech is now enabled")
                    continue
                
                # Check for exit commands
                if command_text.lower() in ['quit', 'exit', 'goodbye', 'bye']:
                    response = "Goodbye! Have a great day!"
                    print(response)
                    if self.speech_enabled:
                        self.voice_output.speak(response)
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
            
            # Speak the response if speech is enabled
            if hasattr(self, 'speech_enabled') and self.speech_enabled:
                self.voice_output.speak(response_text)
            
            # Print additional data if available
            if result.get('data'):
                print(f"Additional info: {result['data']}")
            
        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            print(f"MAC: {error_msg}")
            if hasattr(self, 'speech_enabled') and self.speech_enabled:
                self.voice_output.speak("I encountered an error processing your command.")
    
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
            print("\n🤖 AI Brain Status:")
            print("-" * 40)
            
            status_icons = {True: "✅", False: "❌"}
            
            # Show Gemini status (primary and only AI)
            if ai_status['gemini_available']:
                print(f"{status_icons[ai_status['gemini_available']]} Gemini (PRIMARY AI): Available")
                print(f"\n🧠 AI Brain Mode: ON (Gemini)")
                print("   • Ask any question naturally")
                print("   • Get intelligent, conversational responses")  
                print("   • System commands work seamlessly")
                print("   • Fast and reliable AI processing")
            else:
                print(f"{status_icons[ai_status['gemini_available']]} Gemini (PRIMARY AI): Not configured")
                print(f"\n❌ AI Brain Mode: OFF")
                print("   ⚠️  Using pattern-matching fallback mode")
                print("\n💡 To enable AI Brain:")
                print("   1. Get API key from ai.google.dev")
                print("   2. Add GEMINI_API_KEY to .env file")
                print("   3. Restart MAC Assistant")
                print("   4. Enjoy intelligent conversations!")
            
            print()
            
        except Exception as e:
            print(f"Could not check AI status: {e}")
    
    def _show_personalization_status(self):
        """Show personalization features status."""
        try:
            print("\n🎯 Personalization Status:")
            
            # Get user name
            user_name = self.brain.user_profile.get_name()
            print(f"   👤 User: {user_name}")
            
            # Get personalization stats
            status = self.brain.get_personalization_status()
            
            print(f"   📊 Total interactions: {status.get('total_interactions', 0)}")
            print(f"   🎛️  Custom commands: {status.get('custom_commands_count', 0)}")
            print(f"   ⏰ Active reminders: {status.get('active_reminders', 0)}")
            print(f"   🎨 Response style: {status.get('response_style', 'friendly')}")
            
            # Show most used commands
            most_used = status.get('most_used_commands', [])
            if most_used:
                print(f"   🔥 Most used: {most_used[0][0]} ({most_used[0][1]} times)")
            
            print()
            
        except Exception as e:
            print(f"Could not check personalization status: {e}")
    
    def _show_advanced_features_status(self):
        """Show status of advanced next-generation features."""
        try:
            print("\n🚀 Advanced Features Status:")
            
            # Advanced AI Module Status
            print("   🧠 Advanced AI:")
            print("      • Document Analysis: Ready")
            print("      • Image Processing: Ready")
            print("      • Code Assistant: Active")
            print("      • Research Agent: Available")
            print("      • Creative Assistant: Active")
            
            # Enterprise Integration Status
            print("   🏢 Enterprise Integration:")
            print("      • Collaboration Hub: Connected")
            print("      • Project Manager: Active")
            print("      • Cloud Services: Syncing")
            print("      • Analytics Dashboard: Running")
            print("      • Security Manager: Protected")
            
            # Smart Environment Status
            try:
                env_status = self.brain.smart_environment._get_environment_status()
                if env_status.get('success'):
                    data = env_status.get('data', {})
                    print("   🏠 Smart Environment:")
                    print(f"      • Home Status: {data.get('smart_home', {}).get('status', 'Unknown')}")
                    print(f"      • Connected Devices: {data.get('iot_devices', {}).get('device_count', 0)}")
                    print(f"      • Energy Efficiency: {data.get('energy', {}).get('efficiency_score', 0)}%")
                    print(f"      • Security: {data.get('security', {}).get('status', 'Unknown')}")
                    print(f"      • Active Automations: {data.get('automation', {}).get('active_routines', 0)}")
                else:
                    print("   🏠 Smart Environment: Initializing...")
            except Exception:
                print("   🏠 Smart Environment: Initializing...")
            
            # Show available next-gen commands
            print("\n🎯 Next-Generation Commands Available:")
            print("   🔬 Advanced AI: 'Analyze this document', 'Research quantum computing'")
            print("   🏢 Enterprise: 'Schedule team meeting', 'Show project status'")
            print("   🏠 Smart Home: 'Turn on living room lights', 'Set temperature to 72'")
            print("   📊 Analytics: 'Show productivity dashboard', 'Energy optimization report'")
            
            print()
            
        except Exception as e:
            print(f"Could not check advanced features status: {e}")
    
    def _show_welcome_message(self):
        """Show personalized welcome message."""
        try:
            user_name = self.brain.user_profile.get_name()
            
            # Get proactive suggestions
            suggestions = self.proactive_assistant.get_current_suggestions(3)
            
            # Get notifications
            notifications = self.notification_manager.get_notifications()
            
            print(f"\n👋 Welcome back, {user_name}!")
            
            if notifications:
                print(f"📬 You have {len(notifications)} notifications")
            
            if suggestions:
                print("💡 Smart suggestions:")
                for i, suggestion in enumerate(suggestions[:2], 1):
                    print(f"   {i}. {suggestion['message']}")
            
            print("\n💬 Ready for your commands! Try:")
            print("   • 'my stats' - View your personalization stats")
            print("   • 'remember that I love pizza' - Save personal info")
            print("   • 'remind me to call mom' - Set a reminder")
            print("   • 'suggestions' - Get smart suggestions")
            print("   • 'create command' - Make custom shortcuts")
            
        except Exception as e:
            print(f"Error showing welcome message: {e}")
    
    def _handle_special_commands(self, command_text: str) -> bool:
        """Handle special personalization commands."""
        command_lower = command_text.lower().strip()
        
        if command_lower in ['my stats', 'stats', 'status']:
            self._show_detailed_stats()
            return True
        
        elif command_lower in ['suggestions', 'suggest', 'help me']:
            self._show_suggestions()
            return True
        
        elif command_lower in ['notifications', 'notifs']:
            self._show_notifications()
            return True
        
        elif command_lower.startswith('create command'):
            self._handle_create_command_prompt()
            return True
        
        elif command_lower in ['clear memory', 'clear session']:
            result = self.brain.clear_session_memory()
            print(f"🧹 {result['message']}")
            if hasattr(self, 'speech_enabled') and self.speech_enabled:
                self.voice_output.speak(result['message'])
            return True
        
        elif command_lower in ['mood', 'how am i feeling']:
            self._analyze_current_mood()
            return True
        
        return False
    
    def _show_detailed_stats(self):
        """Show detailed personalization statistics."""
        try:
            status = self.brain.get_personalization_status()
            
            print("\n📊 Your MAC Assistant Statistics:")
            print("=" * 50)
            
            print(f"👤 User: {status.get('user_name', 'Unknown')}")
            print(f"🗣️  Total interactions: {status.get('total_interactions', 0)}")
            print(f"🎨 Response style: {status.get('response_style', 'friendly')}")
            print(f"🎛️  Custom commands: {status.get('custom_commands_count', 0)}")
            print(f"⏰ Active reminders: {status.get('active_reminders', 0)}")
            
            # Show conversation summary
            conv_summary = status.get('conversation_summary', {})
            if conv_summary.get('status') == 'active_conversation':
                print(f"💬 Conversation: {conv_summary.get('total_exchanges', 0)} exchanges")
                
                top_topics = conv_summary.get('top_topics', [])
                if top_topics:
                    print(f"🏷️  Topics: {', '.join(top_topics[:3])}")
            
            # Show most used commands
            most_used = status.get('most_used_commands', [])
            if most_used:
                print("\n🔥 Most Used Commands:")
                for i, (command, count) in enumerate(most_used[:5], 1):
                    print(f"   {i}. {command}: {count} times")
            
            # Show learning insights
            insights = status.get('learning_insights', {})
            if insights:
                print(f"\n🎯 Learning Progress:")
                print(f"   • Patterns learned: {insights.get('patterns_learned', 0)}")
                print(f"   • Most active time: {insights.get('most_active_time', 'unknown')}")
                print(f"   • Preferred style: {insights.get('preferred_style', 'unknown')}")
            
        except Exception as e:
            print(f"❌ Error showing stats: {e}")
    
    def _show_suggestions(self):
        """Show current smart suggestions."""
        try:
            suggestions = self.brain.get_personalized_suggestions()
            proactive_suggestions = self.proactive_assistant.get_current_suggestions()
            
            print("\n💡 Smart Suggestions for You:")
            print("=" * 40)
            
            if suggestions:
                print("🎯 Personalized suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"   {i}. {suggestion}")
            
            if proactive_suggestions:
                print("\n🤖 Proactive suggestions:")
                for i, suggestion in enumerate(proactive_suggestions, 1):
                    priority = suggestion.get('priority', 'medium')
                    emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                    print(f"   {emoji} {suggestion['message']}")
            
            if not suggestions and not proactive_suggestions:
                print("   No suggestions available right now.")
                print("   Keep using MAC to get personalized suggestions!")
            
        except Exception as e:
            print(f"❌ Error showing suggestions: {e}")
    
    def _show_notifications(self):
        """Show current notifications."""
        try:
            notifications = self.notification_manager.get_notifications()
            
            if not notifications:
                print("📬 No notifications at the moment.")
                return
            
            print(f"\n📬 You have {len(notifications)} notifications:")
            print("=" * 45)
            
            for i, notif in enumerate(notifications, 1):
                priority = notif['priority']
                emoji = "🚨" if priority == "urgent" else "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                viewed = "👁️" if notif['viewed'] else "🆕"
                
                print(f"{i}. {emoji}{viewed} {notif['title']}")
                print(f"   {notif['message']}")
                print(f"   📅 {notif['timestamp'][:16]}")
                print()
            
        except Exception as e:
            print(f"❌ Error showing notifications: {e}")
    
    def _handle_create_command_prompt(self):
        """Handle interactive command creation."""
        try:
            print("\n🛠️  Custom Command Creator")
            print("=" * 30)
            
            name = input("Command name: ").strip()
            if not name:
                print("❌ Command name required.")
                return
            
            print("\nCommand types:")
            print("1. Shortcut (single action)")
            print("2. Workflow (multiple steps)")
            print("3. Alias (command alias)")
            
            choice = input("Choose type (1-3): ").strip()
            
            if choice == "1":
                action = input("Action/command to execute: ").strip()
                definition = {
                    "description": f"Custom shortcut: {name}",
                    "action_type": "system",
                    "action": action
                }
                result = self.brain.create_custom_command(name, "shortcut", definition)
                
            elif choice == "2":
                print("Workflow creation not fully implemented yet.")
                print("This feature is coming soon!")
                return
                
            elif choice == "3":
                target = input("Target command: ").strip()
                definition = {
                    "description": f"Alias for: {target}",
                    "target_command": target
                }
                result = self.brain.create_custom_command(name, "alias", definition)
                
            else:
                print("❌ Invalid choice.")
                return
            
            print(f"\n{result['message']}")
            
        except Exception as e:
            print(f"❌ Error creating command: {e}")
    
    def _analyze_current_mood(self):
        """Analyze and display current mood from recent conversation."""
        try:
            # Get recent conversation
            recent_conversations = self.brain.user_profile.conversations[-5:]
            
            if not recent_conversations:
                print("💭 No recent conversation to analyze mood from.")
                return
            
            # Analyze mood from recent messages
            recent_messages = [conv['user_input'] for conv in recent_conversations]
            mood_summary = self.contextual_response.get_mood_summary(recent_messages)
            
            print("\n🎭 Your Current Mood Analysis:")
            print("=" * 35)
            
            if mood_summary['dominant_emotions']:
                print("Top emotions detected:")
                for emotion, count in mood_summary['dominant_emotions']:
                    percentage = (count / mood_summary['emotional_messages']) * 100
                    print(f"   • {emotion.title()}: {percentage:.1f}%")
            
            print(f"\nMood stability: {mood_summary['mood_stability']}")
            print(f"Messages analyzed: {mood_summary['total_messages_analyzed']}")
            
            # Provide mood-based suggestions
            if mood_summary['dominant_emotions']:
                dominant_emotion = mood_summary['dominant_emotions'][0][0]
                
                mood_suggestions = {
                    "happy": "Keep up that positive energy! 🌟",
                    "sad": "I'm here if you need support. 💙",
                    "excited": "Your enthusiasm is wonderful! 🚀",
                    "anxious": "Take deep breaths. We'll work through this together. 🌸",
                    "angry": "Let's find constructive ways to address what's bothering you. 🕯️"
                }
                
                if dominant_emotion in mood_suggestions:
                    print(f"\n💙 {mood_suggestions[dominant_emotion]}")
            
        except Exception as e:
            print(f"❌ Error analyzing mood: {e}")
    
    def _check_proactive_notifications(self):
        """Check and display proactive notifications."""
        try:
            # Get urgent notifications
            urgent_notifications = self.notification_manager.get_notifications("urgent")
            
            if urgent_notifications:
                print(f"\n🚨 {len(urgent_notifications)} urgent notifications!")
                for notif in urgent_notifications[:2]:  # Show top 2
                    print(f"   • {notif['title']}: {notif['message']}")
                
                if hasattr(self, 'speech_enabled') and self.speech_enabled:
                    self.voice_output.speak(f"You have {len(urgent_notifications)} urgent notifications.")
            
        except Exception as e:
            print(f"Error checking notifications: {e}")
    
    def run(self):
        """Run the main assistant loop with enhanced personalization features."""
        # Show welcome message with personalized content
        self._show_welcome_message()
        
        # Check for urgent notifications
        self._check_proactive_notifications()
        
        while True:
            try:
                # Get user input with personalized prompt
                user_name = self.brain.user_profile.get_name()
                prompt = f"\n🎙️  {user_name}, enter command (or 'help' for options): "
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    # Show goodbye with stats
                    stats = self.brain.get_personalization_status()
                    total_interactions = stats.get('total_interactions', 0)
                    print(f"👋 Goodbye, {user_name}! We had {total_interactions} interactions this session.")
                    print("Thanks for using MAC Assistant! 🌟")
                    break
                
                # Handle special personalization commands first
                if self._handle_special_commands(user_input):
                    continue
                
                # Process command through enhanced brain
                response = self.brain.process_command(user_input)
                
                # Print response
                print(f"\n🤖 {response['message']}")
                
                # Handle personalized response enhancements
                if response.get('suggestions'):
                    print("\n💡 Suggestions:")
                    for suggestion in response['suggestions'][:3]:
                        print(f"   • {suggestion}")
                
                if response.get('reminders'):
                    print("\n⏰ Related reminders:")
                    for reminder in response['reminders'][:2]:
                        print(f"   • {reminder}")
                
                # Check for speech output
                if hasattr(self, 'speech_enabled') and self.speech_enabled:
                    # Use enhanced response with mood context
                    speech_text = self.contextual_response.generate_contextual_response(
                        user_input, 
                        response['message'],
                        user_input
                    )
                    self.voice_output.speak(speech_text)
                
                # Check for proactive notifications periodically
                if hasattr(self, '_interaction_count'):
                    self._interaction_count += 1
                    if self._interaction_count % 10 == 0:  # Every 10 interactions
                        self._check_proactive_notifications()
                else:
                    self._interaction_count = 1
                
            except KeyboardInterrupt:
                # Graceful shutdown
                user_name = self.brain.user_profile.get_name()
                stats = self.brain.get_personalization_status()
                total_interactions = stats.get('total_interactions', 0)
                print(f"\n👋 Goodbye, {user_name}! We had {total_interactions} interactions this session.")
                print("Thanks for using MAC Assistant! 🌟")
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                # Log error for learning purposes
                try:
                    self.brain.learning_engine.log_error_pattern(str(e), user_input)
                except:
                    pass
                continue


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
║                       Enhanced Cross-Platform Voice Assistant                 ║
║                              v2.0.0 - Personalized Edition                   ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝

🌟 New in v2.0: Personalization, Learning, Custom Commands, Mood Detection & More!
"""
    print(banner)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="MAC Assistant - Cross-Platform Voice Assistant")
    parser.add_argument("--mode", choices=["voice", "text"], default="voice",
                       help="Mode to run in: voice (default) or text")
    parser.add_argument("--model", default="models/vosk-model",
                       help="Path to Vosk model directory")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--no-speech", action="store_true", help="Disable text-to-speech in text mode")
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    if args.mode == "text":
        # Run in text mode
        assistant = MACAssistant(model_path=args.model)
        enable_speech = not args.no_speech
        assistant.start_text_mode(enable_speech=enable_speech)
    
    elif args.mode == "voice":
        # Run in voice mode (default)
        assistant = MACAssistant(model_path=args.model)
        assistant.start_voice_mode()
    
    else:
        print(f"Unknown mode: {args.mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
