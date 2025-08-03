# MAC Assistant - AI Integration Guide

## Overview

MAC Assistant now includes powerful AI integration capabilities that allow it to answer general questions, search the web, and find YouTube videos beyond the basic predefined commands.

## AI Features

### 🤖 ChatGPT Integration
- **Purpose**: Answer general questions using OpenAI's GPT models
- **Commands**: Any question not matching predefined patterns
- **Examples**:
  - "What is quantum physics?"
  - "Explain machine learning"
  - "How do I cook pasta?"

### 🔍 Web Search
- **Purpose**: Search for information on the web
- **Commands**: Search queries and information requests
- **Examples**:
  - "search for artificial intelligence"
  - "what is Python programming"
  - "tell me about space exploration"
  - "who is Elon Musk"

### 📺 YouTube Search
- **Purpose**: Find YouTube videos on any topic
- **Commands**: Video-related queries
- **Examples**:
  - "youtube machine learning tutorials"
  - "find video about cooking"
  - "search video Python programming"

### 🌤️ Weather Information
- **Purpose**: Get current weather conditions
- **Commands**: Weather-related queries
- **Examples**:
  - "weather forecast"
  - "what's the temperature"
  - "how's the weather"

## Setup Instructions

### 1. Environment Variables

Copy the `.env.template` file to `.env`:
```bash
cp .env.template .env
```

### 2. API Keys Configuration

Edit the `.env` file and add your API keys:

```bash
# Required for ChatGPT (recommended)
OPENAI_API_KEY=your_openai_api_key_here

# Optional for enhanced Google search
SERPAPI_KEY=your_serpapi_key_here

# Optional for YouTube search (uses free alternative if not provided)
YOUTUBE_API_KEY=your_youtube_api_key_here

# Optional for weather information
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

### 3. Getting API Keys

#### OpenAI API Key (Recommended)
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account or sign in
3. Generate a new API key
4. Add billing information (required for usage)

#### SerpAPI Key (Optional)
1. Visit [SerpAPI](https://serpapi.com/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Free tier includes 100 searches per month

#### YouTube API Key (Optional)
1. Visit [Google Cloud Console](https://console.developers.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create credentials (API key)

#### OpenWeatherMap API Key (Optional)
1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Free tier includes 1000 calls per day

## How It Works

### Command Processing Flow

1. **Pattern Matching**: First, MAC tries to match your input against predefined command patterns
2. **AI Services**: If no pattern matches, it falls back to AI services:
   - **Search Detection**: Looks for search-related keywords
   - **YouTube Detection**: Identifies video-related requests
   - **ChatGPT Fallback**: Uses ChatGPT for general questions
   - **Web Search Fallback**: Uses DuckDuckGo as last resort

### Fallback Hierarchy

```
User Input
    ↓
Predefined Patterns (time, weather, etc.)
    ↓ (if no match)
AI Pattern Detection (search, youtube, ai_question)
    ↓ (if no match)
ChatGPT General Response
    ↓ (if unavailable)
Web Search Fallback
    ↓ (if fails)
Unknown Command Message
```

## Usage Examples

### Basic Commands (No API Keys Required)
```
User: "what time is it"
MAC: "The current time is 02:45 PM on Sunday, August 03, 2025"

User: "hello"
MAC: "Good afternoon! I'm MAC, your voice assistant. How can I help you today?"
```

### AI-Powered Responses (Requires API Keys)
```
User: "what is machine learning"
MAC: "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed..."

User: "search for latest news"
MAC: "I found information about latest news: Breaking news updates from around the world including politics, technology, sports..."

User: "youtube python tutorials"
MAC: "I found 3 YouTube videos for 'python tutorials': 'Python Tutorial for Beginners' by Programming with Mosh; 'Learn Python in 4 Hours' by FreeCodeCamp..."
```

### Graceful Degradation
Even without API keys, MAC provides helpful responses:
```
User: "what is artificial intelligence"
MAC: "I searched for 'artificial intelligence' but couldn't find a specific instant answer. You might want to try a web search engine for more detailed results."
```

## Available Commands

### Traditional Commands
- **Time**: "what time is it", "current time"
- **Greeting**: "hello", "hi", "good morning"
- **System**: "system info", "computer info"
- **Volume**: "volume up", "volume down", "mute"
- **Applications**: "open app", "close app"
- **Shutdown**: "shutdown", "restart", "sleep"

### AI-Enhanced Commands
- **Search**: "search for [topic]", "what is [something]", "tell me about [topic]"
- **YouTube**: "youtube [topic]", "find video about [topic]"
- **Weather**: "weather", "temperature", "forecast"
- **General Questions**: Any question not matching above patterns

## Tips for Best Results

1. **Be Specific**: "search for Python web frameworks" works better than "Python stuff"
2. **Use Natural Language**: "what is the weather like" is fine, no need for rigid commands
3. **Try Different Phrasings**: If one way doesn't work, try rephrasing your question
4. **Check AI Status**: Run MAC to see which AI services are available

## Troubleshooting

### Common Issues

1. **"AI service not available"**
   - Check your `.env` file exists and has valid API keys
   - Verify your OpenAI account has billing set up

2. **"Search service temporarily unavailable"**
   - Check your internet connection
   - Try again in a few moments

3. **"YouTube search error"**
   - This might use a fallback message due to library limitations
   - The core functionality still works

### Debug Mode

Run with debug info to see what's happening:
```bash
python main.py --mode text --debug
```

## Security Notes

- Never commit your `.env` file with real API keys to version control
- Keep your API keys secure and don't share them
- Monitor your API usage to avoid unexpected charges
- Free tiers are usually sufficient for personal use

## Next Steps

1. Set up your API keys for full functionality
2. Try various commands to explore capabilities
3. Use voice mode for hands-free interaction
4. Integrate with other services as needed

For more information, see the main documentation in the `docs/` folder.
