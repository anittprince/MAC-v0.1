"""
MAC Assistant - AI Services Integration
Integrates external AI services like ChatGPT, Google Search, and YouTube.
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIServices:
    def __init__(self):
        """Initialize AI services with API keys."""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.serpapi_key = os.getenv('SERPAPI_KEY')
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        
        # Initialize OpenAI
        if self.openai_api_key:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                print("✓ OpenAI ChatGPT initialized")
            except Exception as e:
                print(f"⚠ OpenAI initialization failed: {e}")
                self.openai_client = None
        else:
            self.openai_client = None
            print("⚠ OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
    
    def ask_chatgpt(self, question: str, context: str = "") -> Dict[str, Any]:
        """
        Ask ChatGPT a question and get a response.
        
        Args:
            question: The question to ask
            context: Additional context for the question
            
        Returns:
            Dictionary with response and metadata
        """
        if not self.openai_client:
            return {
                'success': False,
                'message': 'ChatGPT is not available. Please set up your OpenAI API key.',
                'data': None
            }
        
        try:
            # Prepare the prompt
            system_prompt = f"""
            You are MAC, a helpful voice assistant. Provide clear, concise, and friendly responses.
            Keep answers conversational and under 100 words for voice responses.
            {context}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            
            return {
                'success': True,
                'message': answer,
                'data': {
                    'source': 'ChatGPT',
                    'model': 'gpt-3.5-turbo',
                    'tokens_used': response.usage.total_tokens
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Sorry, I encountered an error asking ChatGPT: {str(e)}',
                'data': None
            }
    
    def search_google(self, query: str, num_results: int = 3) -> Dict[str, Any]:
        """
        Search Google and return results.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            Dictionary with search results
        """
        if not self.serpapi_key:
            # Fallback to simple web search without API
            return self._simple_web_search(query)
        
        try:
            from serpapi import GoogleSearch
            
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "num": num_results
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "organic_results" in results:
                search_results = []
                for result in results["organic_results"][:num_results]:
                    search_results.append({
                        'title': result.get('title', ''),
                        'snippet': result.get('snippet', ''),
                        'link': result.get('link', '')
                    })
                
                # Create a summary
                summary = f"I found {len(search_results)} results for '{query}': "
                summary += ". ".join([r['snippet'][:100] + "..." for r in search_results if r['snippet']])
                
                return {
                    'success': True,
                    'message': summary[:300] + "..." if len(summary) > 300 else summary,
                    'data': {
                        'source': 'Google Search',
                        'results': search_results,
                        'query': query
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f'No results found for "{query}"',
                    'data': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Sorry, I encountered an error searching Google: {str(e)}',
                'data': None
            }
    
    def _simple_web_search(self, query: str) -> Dict[str, Any]:
        """
        Simple web search without API (fallback method).
        """
        try:
            # Use DuckDuckGo instant answer API
            import urllib.parse
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
            
            headers = {
                'User-Agent': 'MAC Assistant 1.0'
            }
            
            response = requests.get(url, timeout=10, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Try to get instant answer
                if data.get('AbstractText'):
                    return {
                        'success': True,
                        'message': data['AbstractText'][:200] + "..." if len(data['AbstractText']) > 200 else data['AbstractText'],
                        'data': {
                            'source': 'DuckDuckGo',
                            'query': query,
                            'url': data.get('AbstractURL', '')
                        }
                    }
                elif data.get('Definition'):
                    return {
                        'success': True,
                        'message': data['Definition'],
                        'data': {
                            'source': 'DuckDuckGo',
                            'query': query,
                            'type': 'definition'
                        }
                    }
                else:
                    # If no instant answer, provide a generic response
                    return {
                        'success': True,
                        'message': f"I searched for '{query}' but couldn't find a specific instant answer. You might want to try a web search engine for more detailed results.",
                        'data': {
                            'source': 'DuckDuckGo',
                            'query': query,
                            'status': 'no_instant_answer'
                        }
                    }
            else:
                return {
                    'success': False,
                    'message': 'Search service is temporarily unavailable.',
                    'data': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'I cannot search for that right now. Error: {str(e)}',
                'data': None
            }
    
    def search_youtube(self, query: str, max_results: int = 3) -> Dict[str, Any]:
        """
        Search YouTube for videos.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            Dictionary with YouTube search results
        """
        try:
            from youtubesearchpython import VideosSearch
            
            # Create search object with simple configuration
            videos_search = VideosSearch(query, limit=max_results)
            
            # Get results
            results = videos_search.result()
            
            if results and 'result' in results and results['result']:
                video_list = []
                for video in results['result']:
                    video_info = {
                        'title': video.get('title', 'Unknown Title'),
                        'channel': video.get('channel', {}).get('name', 'Unknown Channel'),
                        'duration': video.get('duration', 'Unknown'),
                        'views': video.get('viewCount', {}).get('text', 'Unknown') if video.get('viewCount') else 'Unknown',
                        'url': video.get('link', '')
                    }
                    video_list.append(video_info)
                
                summary = f"I found {len(video_list)} YouTube videos for '{query}': "
                video_titles = [f'"{v["title"]}" by {v["channel"]}' for v in video_list]
                summary += "; ".join(video_titles[:2])  # Show first 2 to avoid too long message
                
                if len(video_list) > 2:
                    summary += f" and {len(video_list) - 2} more."
                
                return {
                    'success': True,
                    'message': summary,
                    'data': {
                        'source': 'YouTube',
                        'videos': video_list,
                        'query': query
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f'No YouTube videos found for "{query}"',
                    'data': None
                }
                
        except ImportError:
            return {
                'success': False,
                'message': 'YouTube search requires the youtubesearchpython package. Please install it.',
                'data': None
            }
        except Exception as e:
            # Fallback to a simple message
            return {
                'success': True,
                'message': f'I would search YouTube for "{query}" videos, but the search service encountered an issue. You can search manually on YouTube.',
                'data': {
                    'source': 'YouTube (fallback)',
                    'query': query,
                    'error': str(e)
                }
            }
    
    def get_weather(self, location: str = "current location") -> Dict[str, Any]:
        """
        Get weather information (using OpenWeatherMap API if available).
        """
        weather_api_key = os.getenv('OPENWEATHER_API_KEY')
        
        if not weather_api_key:
            return {
                'success': False,
                'message': 'Weather service requires API key. Please set OPENWEATHER_API_KEY.',
                'data': None
            }
        
        try:
            if location == "current location":
                # Get location by IP
                ip_response = requests.get('http://ip-api.com/json/', timeout=5)
                if ip_response.status_code == 200:
                    location_data = ip_response.json()
                    location = f"{location_data.get('city', '')},{location_data.get('country', '')}"
            
            # Get weather data
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_api_key}&units=metric"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                temp = data['main']['temp']
                description = data['weather'][0]['description']
                humidity = data['main']['humidity']
                city = data['name']
                
                message = f"The weather in {city} is {description} with a temperature of {temp}°C and {humidity}% humidity."
                
                return {
                    'success': True,
                    'message': message,
                    'data': {
                        'source': 'OpenWeatherMap',
                        'location': city,
                        'temperature': temp,
                        'description': description,
                        'humidity': humidity
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f'Could not get weather for {location}',
                    'data': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Weather service error: {str(e)}',
                'data': None
            }
    
    def is_available(self) -> Dict[str, bool]:
        """Check which services are available."""
        return {
            'chatgpt': bool(self.openai_client),
            'google_search': bool(self.serpapi_key),
            'youtube_search': True,  # Uses free API
            'weather': bool(os.getenv('OPENWEATHER_API_KEY')),
            'fallback_search': True  # DuckDuckGo
        }
