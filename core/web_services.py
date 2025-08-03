"""
MAC Assistant - Web Services Integration
Email, weather, news, and web automation capabilities.
"""

import requests
import json
import os
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Optional import for RSS feeds
try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False

class WebServicesManager:
    """Manage web services and API integrations."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize web services manager."""
        self.data_dir = data_dir
        self.config_file = os.path.join(data_dir, "web_services_config.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize services
        self.weather_service = WeatherService(self.config.get('weather', {}))
        self.news_service = NewsService(self.config.get('news', {}))
        self.email_service = EmailService(self.config.get('email', {}))
    
    def _load_config(self) -> Dict:
        """Load web services configuration."""
        if not os.path.exists(self.config_file):
            # Create default config
            default_config = {
                "weather": {
                    "api_key": "",
                    "default_city": "New York",
                    "units": "metric"
                },
                "news": {
                    "api_key": "",
                    "default_sources": ["bbc-news", "reuters", "associated-press"],
                    "default_category": "general"
                },
                "email": {
                    "smtp_server": "",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "use_tls": True
                }
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading web services config: {e}")
            return {}
    
    def process_web_command(self, command: str) -> Dict[str, Any]:
        """Process web-related commands."""
        command_lower = command.lower().strip()
        
        # Weather commands
        if any(keyword in command_lower for keyword in ['weather', 'temperature', 'forecast']):
            return self.weather_service.handle_weather_command(command)
        
        # News commands
        elif any(keyword in command_lower for keyword in ['news', 'headlines', 'latest news']):
            return self.news_service.handle_news_command(command)
        
        # Email commands
        elif any(keyword in command_lower for keyword in ['send email', 'email', 'compose']):
            return self.email_service.handle_email_command(command)
        
        # Web search commands
        elif any(keyword in command_lower for keyword in ['search', 'look up', 'find information']):
            return self._handle_web_search(command)
        
        else:
            return {
                'success': False,
                'message': "🌐 I don't recognize that web command. Try asking about weather, news, or email."
            }
    
    def _handle_web_search(self, command: str) -> Dict[str, Any]:
        """Handle web search requests."""
        # Extract search query
        search_query = re.sub(r'\b(search|look up|find information about|find)\b', '', command, flags=re.IGNORECASE).strip()
        
        if not search_query:
            return {
                'success': False,
                'message': "❓ What would you like me to search for?"
            }
        
        # For now, provide search suggestions
        return {
            'success': True,
            'message': f"🔍 Here are some search suggestions for '{search_query}':",
            'suggestions': [
                f"Google: https://www.google.com/search?q={search_query.replace(' ', '+')}",
                f"Wikipedia: https://en.wikipedia.org/wiki/{search_query.replace(' ', '_')}",
                f"YouTube: https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
            ]
        }

class WeatherService:
    """Weather information service."""
    
    def __init__(self, config: Dict):
        """Initialize weather service."""
        self.api_key = config.get('api_key', '')
        self.default_city = config.get('default_city', 'New York')
        self.units = config.get('units', 'metric')
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def handle_weather_command(self, command: str) -> Dict[str, Any]:
        """Handle weather-related commands."""
        if not self.api_key:
            return {
                'success': False,
                'message': "🌤️ Weather service not configured. Please add your OpenWeatherMap API key to enable weather features."
            }
        
        # Extract city from command (basic approach)
        city = self._extract_city_from_command(command) or self.default_city
        
        # Determine request type
        if 'forecast' in command.lower():
            return self.get_forecast(city)
        else:
            return self.get_current_weather(city)
    
    def _extract_city_from_command(self, command: str) -> Optional[str]:
        """Extract city name from weather command."""
        # Look for patterns like "weather in [city]" or "weather for [city]"
        patterns = [
            r'weather (?:in|for) (.+)',
            r'temperature (?:in|for) (.+)',
            r'forecast (?:in|for) (.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city."""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': self.units
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                humidity = data['main']['humidity']
                description = data['weather'][0]['description'].title()
                
                unit_symbol = "°C" if self.units == "metric" else "°F"
                
                return {
                    'success': True,
                    'message': f"🌤️ Weather in {city}:\n"
                              f"🌡️ Temperature: {temp}{unit_symbol} (feels like {feels_like}{unit_symbol})\n"
                              f"☁️ Conditions: {description}\n"
                              f"💧 Humidity: {humidity}%",
                    'data': {
                        'city': city,
                        'temperature': temp,
                        'feels_like': feels_like,
                        'description': description,
                        'humidity': humidity
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f"❌ Could not get weather for {city}. Please check the city name."
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Weather service error: {str(e)}"
            }
    
    def get_forecast(self, city: str, days: int = 3) -> Dict[str, Any]:
        """Get weather forecast for a city."""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': self.units
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                forecasts = []
                
                # Group by day and take first forecast for each day
                current_date = None
                for item in data['list'][:days * 8]:  # 8 forecasts per day (every 3 hours)
                    forecast_date = datetime.fromtimestamp(item['dt']).date()
                    
                    if forecast_date != current_date:
                        temp = item['main']['temp']
                        description = item['weather'][0]['description'].title()
                        unit_symbol = "°C" if self.units == "metric" else "°F"
                        
                        forecasts.append({
                            'date': forecast_date.strftime('%A, %B %d'),
                            'temperature': f"{temp}{unit_symbol}",
                            'description': description
                        })
                        
                        current_date = forecast_date
                        
                        if len(forecasts) >= days:
                            break
                
                forecast_text = f"📅 {days}-day forecast for {city}:\n"
                for forecast in forecasts:
                    forecast_text += f"• {forecast['date']}: {forecast['temperature']}, {forecast['description']}\n"
                
                return {
                    'success': True,
                    'message': forecast_text.strip(),
                    'data': {
                        'city': city,
                        'forecasts': forecasts
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f"❌ Could not get forecast for {city}. Please check the city name."
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Weather forecast error: {str(e)}"
            }

class NewsService:
    """News and information service."""
    
    def __init__(self, config: Dict):
        """Initialize news service."""
        self.api_key = config.get('api_key', '')
        self.default_sources = config.get('default_sources', ['bbc-news'])
        self.default_category = config.get('default_category', 'general')
        self.base_url = "https://newsapi.org/v2"
    
    def handle_news_command(self, command: str) -> Dict[str, Any]:
        """Handle news-related commands."""
        if not self.api_key:
            # Fallback to RSS feeds
            return self.get_rss_headlines()
        
        # Extract category or topic from command
        category = self._extract_news_category(command)
        
        return self.get_headlines(category=category)
    
    def _extract_news_category(self, command: str) -> Optional[str]:
        """Extract news category from command."""
        categories = ['business', 'technology', 'sports', 'health', 'science', 'entertainment']
        
        command_lower = command.lower()
        for category in categories:
            if category in command_lower:
                return category
        
        return self.default_category
    
    def get_headlines(self, category: str = None, count: int = 5) -> Dict[str, Any]:
        """Get news headlines."""
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                'apiKey': self.api_key,
                'pageSize': count,
                'country': 'us'
            }
            
            if category:
                params['category'] = category
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if not articles:
                    return {
                        'success': False,
                        'message': "📰 No news articles found."
                    }
                
                headlines_text = f"📰 Latest {'(' + category + ') ' if category else ''}Headlines:\n\n"
                headlines_data = []
                
                for i, article in enumerate(articles, 1):
                    title = article['title']
                    source = article['source']['name']
                    url = article['url']
                    
                    headlines_text += f"{i}. {title}\n   📍 {source}\n\n"
                    headlines_data.append({
                        'title': title,
                        'source': source,
                        'url': url
                    })
                
                return {
                    'success': True,
                    'message': headlines_text.strip(),
                    'data': {
                        'category': category,
                        'articles': headlines_data
                    }
                }
            else:
                return {
                    'success': False,
                    'message': "❌ Could not fetch news headlines."
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ News service error: {str(e)}"
            }
    
    def get_rss_headlines(self, count: int = 5) -> Dict[str, Any]:
        """Get headlines from RSS feeds (fallback when no API key)."""
        if not FEEDPARSER_AVAILABLE:
            return {
                'success': False,
                'message': "📰 RSS feed support not available. Please install feedparser: pip install feedparser"
            }
        
        try:
            # Use BBC RSS feed as fallback
            rss_url = "http://feeds.bbci.co.uk/news/rss.xml"
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                return {
                    'success': False,
                    'message': "📰 Could not fetch news from RSS feed."
                }
            
            headlines_text = "📰 Latest Headlines (BBC):\n\n"
            headlines_data = []
            
            for i, entry in enumerate(feed.entries[:count], 1):
                title = entry.title
                link = entry.link
                
                headlines_text += f"{i}. {title}\n"
                headlines_data.append({
                    'title': title,
                    'source': 'BBC',
                    'url': link
                })
            
            return {
                'success': True,
                'message': headlines_text.strip(),
                'data': {
                    'source': 'RSS',
                    'articles': headlines_data
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ RSS news error: {str(e)}"
            }

class EmailService:
    """Email management service."""
    
    def __init__(self, config: Dict):
        """Initialize email service."""
        self.smtp_server = config.get('smtp_server', '')
        self.smtp_port = config.get('smtp_port', 587)
        self.username = config.get('username', '')
        self.password = config.get('password', '')
        self.use_tls = config.get('use_tls', True)
    
    def handle_email_command(self, command: str) -> Dict[str, Any]:
        """Handle email-related commands."""
        if not self.smtp_server or not self.username:
            return {
                'success': False,
                'message': "📧 Email service not configured. Please add your SMTP settings to enable email features."
            }
        
        # For now, provide email composition guidance
        return {
            'success': True,
            'message': "📧 Email features are configured but composition interface is not yet implemented.\n"
                      "This feature will allow you to:\n"
                      "• Compose and send emails\n"
                      "• Manage email templates\n"
                      "• Schedule email sending\n"
                      "• Integration with contacts",
            'suggestions': [
                "Try: 'compose email to john@example.com'",
                "Try: 'send email reminder about meeting'",
                "Try: 'check email settings'"
            ]
        }
    
    def send_email(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """Send an email."""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.use_tls:
                server.starttls()
            
            server.login(self.username, self.password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.username, to_email, text)
            server.quit()
            
            return {
                'success': True,
                'message': f"✅ Email sent successfully to {to_email}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Failed to send email: {str(e)}"
            }
