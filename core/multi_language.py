"""
MAC Assistant - Multi-language Support Module
Advanced translation, localization, and cross-language communication capabilities.
"""

import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class LanguageProfile:
    """Language profile for user preferences."""
    primary_language: str
    secondary_languages: List[str]
    accent_preference: str
    formality_level: str
    cultural_context: str
    translation_preferences: Dict[str, str]

@dataclass
class TranslationResult:
    """Result of translation operation."""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    translation_type: str
    metadata: Dict[str, Any]

class MultiLanguageManager:
    """Manages multi-language support and translation capabilities."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize multi-language manager."""
        self.data_dir = Path(data_dir)
        self.language_dir = self.data_dir / "languages"
        self.language_dir.mkdir(parents=True, exist_ok=True)
        
        # Database and storage
        self.language_db = self.language_dir / "language_data.db"
        self.translations_cache = self.language_dir / "translations_cache.json"
        self.localization_dir = self.language_dir / "localization"
        self.localization_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self._init_language_db()
        self.translator = TranslationEngine(self.language_dir)
        self.localizer = LocalizationManager(self.localization_dir)
        self.language_detector = LanguageDetector()
        self.cultural_adapter = CulturalContextAdapter()
        
        # Supported languages
        self.supported_languages = {
            'en': {'name': 'English', 'native': 'English', 'family': 'Germanic'},
            'es': {'name': 'Spanish', 'native': 'Español', 'family': 'Romance'},
            'fr': {'name': 'French', 'native': 'Français', 'family': 'Romance'},
            'de': {'name': 'German', 'native': 'Deutsch', 'family': 'Germanic'},
            'zh': {'name': 'Chinese', 'native': '中文', 'family': 'Sino-Tibetan'},
            'ja': {'name': 'Japanese', 'native': '日本語', 'family': 'Japonic'},
            'ko': {'name': 'Korean', 'native': '한국어', 'family': 'Koreanic'},
            'ar': {'name': 'Arabic', 'native': 'العربية', 'family': 'Semitic'},
            'hi': {'name': 'Hindi', 'native': 'हिन्दी', 'family': 'Indo-European'},
            'pt': {'name': 'Portuguese', 'native': 'Português', 'family': 'Romance'},
            'ru': {'name': 'Russian', 'native': 'Русский', 'family': 'Slavic'},
            'it': {'name': 'Italian', 'native': 'Italiano', 'family': 'Romance'},
            'nl': {'name': 'Dutch', 'native': 'Nederlands', 'family': 'Germanic'},
            'sv': {'name': 'Swedish', 'native': 'Svenska', 'family': 'Germanic'},
            'da': {'name': 'Danish', 'native': 'Dansk', 'family': 'Germanic'},
            'no': {'name': 'Norwegian', 'native': 'Norsk', 'family': 'Germanic'},
            'fi': {'name': 'Finnish', 'native': 'Suomi', 'family': 'Uralic'},
            'pl': {'name': 'Polish', 'native': 'Polski', 'family': 'Slavic'},
            'tr': {'name': 'Turkish', 'native': 'Türkçe', 'family': 'Turkic'},
            'th': {'name': 'Thai', 'native': 'ไทย', 'family': 'Tai-Kadai'}
        }
        
        # Load user language profile
        self.user_language_profile = self._load_user_language_profile()
    
    def _init_language_db(self):
        """Initialize language database."""
        conn = sqlite3.connect(self.language_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_text TEXT,
                translated_text TEXT,
                source_language TEXT,
                target_language TEXT,
                translation_type TEXT,
                confidence REAL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS language_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT,
                detected_language TEXT,
                response_language TEXT,
                interaction_type TEXT,
                success BOOLEAN,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_language_preferences (
                id INTEGER PRIMARY KEY,
                primary_language TEXT,
                secondary_languages TEXT,
                accent_preference TEXT,
                formality_level TEXT,
                cultural_context TEXT,
                preferences TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def translate_text(self, text: str, target_language: str, source_language: str = None) -> Dict[str, Any]:
        """Translate text to target language."""
        try:
            # Detect source language if not provided
            if not source_language:
                detection_result = self.language_detector.detect_language(text)
                source_language = detection_result['language']
                confidence = detection_result['confidence']
            else:
                confidence = 1.0
            
            # Validate languages
            if target_language not in self.supported_languages:
                return {
                    'success': False,
                    'message': f"Target language '{target_language}' not supported"
                }
            
            if source_language not in self.supported_languages:
                return {
                    'success': False,
                    'message': f"Source language '{source_language}' not supported"
                }
            
            # Skip translation if same language
            if source_language == target_language:
                return {
                    'success': True,
                    'message': f"🌍 Text is already in {self.supported_languages[target_language]['name']}",
                    'data': {
                        'original_text': text,
                        'translated_text': text,
                        'source_language': source_language,
                        'target_language': target_language,
                        'confidence': 1.0
                    }
                }
            
            # Perform translation
            translation_result = self.translator.translate(text, source_language, target_language)
            
            if translation_result['success']:
                # Save translation to database
                self._save_translation(TranslationResult(
                    original_text=text,
                    translated_text=translation_result['translated_text'],
                    source_language=source_language,
                    target_language=target_language,
                    confidence=translation_result['confidence'],
                    translation_type='text',
                    metadata={'method': translation_result.get('method', 'unknown')}
                ))
                
                source_name = self.supported_languages[source_language]['name']
                target_name = self.supported_languages[target_language]['name']
                
                return {
                    'success': True,
                    'message': f"🌍 Translated from {source_name} to {target_name}:\n\n"
                              f"📝 Original: {text}\n"
                              f"🔄 Translation: {translation_result['translated_text']}",
                    'data': {
                        'original_text': text,
                        'translated_text': translation_result['translated_text'],
                        'source_language': source_language,
                        'target_language': target_language,
                        'source_language_name': source_name,
                        'target_language_name': target_name,
                        'confidence': translation_result['confidence']
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f"Translation failed: {translation_result.get('error', 'Unknown error')}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Translation error: {str(e)}"
            }
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect the language of input text."""
        try:
            result = self.language_detector.detect_language(text)
            
            if result['success']:
                language_code = result['language']
                confidence = result['confidence']
                
                if language_code in self.supported_languages:
                    language_info = self.supported_languages[language_code]
                    
                    return {
                        'success': True,
                        'message': f"🔍 Language detected: {language_info['name']} ({language_info['native']})\n"
                                  f"📊 Confidence: {confidence:.1%}",
                        'data': {
                            'language_code': language_code,
                            'language_name': language_info['name'],
                            'native_name': language_info['native'],
                            'language_family': language_info['family'],
                            'confidence': confidence,
                            'text_sample': text[:100] + ('...' if len(text) > 100 else '')
                        }
                    }
                else:
                    return {
                        'success': True,
                        'message': f"🔍 Language detected: {language_code} (confidence: {confidence:.1%})\n"
                                  f"⚠️ This language is not in our supported list",
                        'data': {
                            'language_code': language_code,
                            'confidence': confidence,
                            'supported': False
                        }
                    }
            else:
                return {
                    'success': False,
                    'message': f"❌ Language detection failed: {result.get('error', 'Unknown error')}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Language detection error: {str(e)}"
            }
    
    def set_primary_language(self, language_code: str) -> Dict[str, Any]:
        """Set user's primary language."""
        try:
            if language_code not in self.supported_languages:
                return {
                    'success': False,
                    'message': f"Language '{language_code}' is not supported"
                }
            
            self.user_language_profile.primary_language = language_code
            self._save_user_language_profile()
            
            language_name = self.supported_languages[language_code]['name']
            native_name = self.supported_languages[language_code]['native']
            
            return {
                'success': True,
                'message': f"🌍 Primary language set to {language_name} ({native_name})",
                'data': {
                    'primary_language': language_code,
                    'language_name': language_name,
                    'native_name': native_name
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Error setting primary language: {str(e)}"
            }
    
    def add_secondary_language(self, language_code: str) -> Dict[str, Any]:
        """Add a secondary language for the user."""
        try:
            if language_code not in self.supported_languages:
                return {
                    'success': False,
                    'message': f"Language '{language_code}' is not supported"
                }
            
            if language_code not in self.user_language_profile.secondary_languages:
                self.user_language_profile.secondary_languages.append(language_code)
                self._save_user_language_profile()
                
                language_name = self.supported_languages[language_code]['name']
                
                return {
                    'success': True,
                    'message': f"🌍 Added {language_name} as secondary language",
                    'data': {
                        'secondary_languages': self.user_language_profile.secondary_languages,
                        'added_language': language_code
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f"Language '{language_code}' is already in your secondary languages"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Error adding secondary language: {str(e)}"
            }
    
    def get_language_profile(self) -> Dict[str, Any]:
        """Get user's language profile and preferences."""
        try:
            primary_lang = self.user_language_profile.primary_language
            secondary_langs = self.user_language_profile.secondary_languages
            
            # Get language names
            primary_name = self.supported_languages.get(primary_lang, {}).get('name', 'Unknown')
            secondary_names = [
                self.supported_languages.get(lang, {}).get('name', 'Unknown') 
                for lang in secondary_langs
            ]
            
            return {
                'success': True,
                'message': f"🌍 Language Profile:\n\n"
                          f"🎯 Primary: {primary_name} ({primary_lang})\n"
                          f"📚 Secondary: {', '.join(secondary_names) if secondary_names else 'None'}\n"
                          f"🎭 Formality: {self.user_language_profile.formality_level}\n"
                          f"🌏 Cultural context: {self.user_language_profile.cultural_context}",
                'data': {
                    'primary_language': primary_lang,
                    'primary_language_name': primary_name,
                    'secondary_languages': secondary_langs,
                    'secondary_language_names': secondary_names,
                    'accent_preference': self.user_language_profile.accent_preference,
                    'formality_level': self.user_language_profile.formality_level,
                    'cultural_context': self.user_language_profile.cultural_context,
                    'translation_preferences': self.user_language_profile.translation_preferences
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Error getting language profile: {str(e)}"
            }
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of all supported languages."""
        try:
            languages_by_family = {}
            
            for code, info in self.supported_languages.items():
                family = info['family']
                if family not in languages_by_family:
                    languages_by_family[family] = []
                
                languages_by_family[family].append({
                    'code': code,
                    'name': info['name'],
                    'native': info['native']
                })
            
            # Sort families and languages
            for family in languages_by_family:
                languages_by_family[family].sort(key=lambda x: x['name'])
            
            total_languages = len(self.supported_languages)
            
            message = f"🌍 Supported Languages ({total_languages} total):\n\n"
            for family, languages in sorted(languages_by_family.items()):
                message += f"📁 {family} Family:\n"
                for lang in languages:
                    message += f"  • {lang['name']} ({lang['native']}) - {lang['code']}\n"
                message += "\n"
            
            return {
                'success': True,
                'message': message.strip(),
                'data': {
                    'total_languages': total_languages,
                    'languages_by_family': languages_by_family,
                    'all_languages': self.supported_languages
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Error getting supported languages: {str(e)}"
            }
    
    def get_translation_history(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent translation history."""
        try:
            conn = sqlite3.connect(self.language_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT original_text, translated_text, source_language, 
                       target_language, confidence, created_at
                FROM translations
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            history = []
            for row in cursor.fetchall():
                source_name = self.supported_languages.get(row[2], {}).get('name', row[2])
                target_name = self.supported_languages.get(row[3], {}).get('name', row[3])
                
                history.append({
                    'original_text': row[0][:50] + ('...' if len(row[0]) > 50 else ''),
                    'translated_text': row[1][:50] + ('...' if len(row[1]) > 50 else ''),
                    'source_language': row[2],
                    'target_language': row[3],
                    'source_name': source_name,
                    'target_name': target_name,
                    'confidence': row[4],
                    'created_at': row[5]
                })
            
            conn.close()
            
            return {
                'success': True,
                'message': f"📊 Translation History ({len(history)} recent translations)",
                'data': {'history': history}
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Error getting translation history: {str(e)}"
            }
    
    def _save_translation(self, result: TranslationResult):
        """Save translation result to database."""
        conn = sqlite3.connect(self.language_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO translations 
            (original_text, translated_text, source_language, target_language, 
             translation_type, confidence, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.original_text,
            result.translated_text,
            result.source_language,
            result.target_language,
            result.translation_type,
            result.confidence,
            json.dumps(result.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def _load_user_language_profile(self) -> LanguageProfile:
        """Load user language profile from database."""
        try:
            conn = sqlite3.connect(self.language_db)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM user_language_preferences WHERE id = 1')
            row = cursor.fetchone()
            
            if row:
                return LanguageProfile(
                    primary_language=row[1] or 'en',
                    secondary_languages=json.loads(row[2] or '[]'),
                    accent_preference=row[3] or 'neutral',
                    formality_level=row[4] or 'casual',
                    cultural_context=row[5] or 'western',
                    translation_preferences=json.loads(row[6] or '{}')
                )
            else:
                # Create default profile
                return LanguageProfile(
                    primary_language='en',
                    secondary_languages=[],
                    accent_preference='neutral',
                    formality_level='casual',
                    cultural_context='western',
                    translation_preferences={}
                )
                
        except Exception:
            # Return default profile on error
            return LanguageProfile(
                primary_language='en',
                secondary_languages=[],
                accent_preference='neutral',
                formality_level='casual',
                cultural_context='western',
                translation_preferences={}
            )
        finally:
            try:
                conn.close()
            except:
                pass
    
    def _save_user_language_profile(self):
        """Save user language profile to database."""
        conn = sqlite3.connect(self.language_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_language_preferences 
            (id, primary_language, secondary_languages, accent_preference, 
             formality_level, cultural_context, preferences)
            VALUES (1, ?, ?, ?, ?, ?, ?)
        ''', (
            self.user_language_profile.primary_language,
            json.dumps(self.user_language_profile.secondary_languages),
            self.user_language_profile.accent_preference,
            self.user_language_profile.formality_level,
            self.user_language_profile.cultural_context,
            json.dumps(self.user_language_profile.translation_preferences)
        ))
        
        conn.commit()
        conn.close()

class TranslationEngine:
    """Core translation engine with multiple backend support."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.cache_file = data_dir / "translation_cache.json"
        self.cache = self._load_cache()
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Translate text using available translation services."""
        try:
            # Check cache first
            cache_key = f"{source_lang}:{target_lang}:{hash(text)}"
            if cache_key in self.cache:
                cached_result = self.cache[cache_key]
                return {
                    'success': True,
                    'translated_text': cached_result['translation'],
                    'confidence': cached_result['confidence'],
                    'method': 'cache'
                }
            
            # Simulate translation (in real implementation, would use Google Translate API, etc.)
            translated_text = self._simulate_translation(text, source_lang, target_lang)
            confidence = 0.9  # Simulated confidence
            
            # Cache the result
            self.cache[cache_key] = {
                'translation': translated_text,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat()
            }
            self._save_cache()
            
            return {
                'success': True,
                'translated_text': translated_text,
                'confidence': confidence,
                'method': 'translation_api'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _simulate_translation(self, text: str, source_lang: str, target_lang: str) -> str:
        """Simulate translation for demonstration purposes."""
        # In real implementation, this would call actual translation APIs
        
        # Simple simulated translations for common phrases
        simulated_translations = {
            ('en', 'es'): {
                'hello': 'hola',
                'goodbye': 'adiós',
                'thank you': 'gracias',
                'please': 'por favor',
                'yes': 'sí',
                'no': 'no'
            },
            ('en', 'fr'): {
                'hello': 'bonjour',
                'goodbye': 'au revoir',
                'thank you': 'merci',
                'please': 's\'il vous plaît',
                'yes': 'oui',
                'no': 'non'
            },
            ('en', 'de'): {
                'hello': 'hallo',
                'goodbye': 'auf wiedersehen',
                'thank you': 'danke',
                'please': 'bitte',
                'yes': 'ja',
                'no': 'nein'
            }
        }
        
        text_lower = text.lower().strip()
        lang_pair = (source_lang, target_lang)
        
        if lang_pair in simulated_translations and text_lower in simulated_translations[lang_pair]:
            return simulated_translations[lang_pair][text_lower]
        else:
            return f"[Translated from {source_lang} to {target_lang}]: {text}"
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load translation cache from file."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_cache(self):
        """Save translation cache to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

class LanguageDetector:
    """Detects language from text input."""
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language from text."""
        try:
            # Simulate language detection
            # In real implementation, would use libraries like langdetect, polyglot, etc.
            
            # Simple pattern-based detection for demonstration
            if re.search(r'[áéíóúñ¿¡]', text.lower()):
                return {'success': True, 'language': 'es', 'confidence': 0.8}
            elif re.search(r'[àâäéèêëïîôöùûüÿç]', text.lower()):
                return {'success': True, 'language': 'fr', 'confidence': 0.8}
            elif re.search(r'[äöüß]', text.lower()):
                return {'success': True, 'language': 'de', 'confidence': 0.8}
            elif re.search(r'[\u4e00-\u9fff]', text):
                return {'success': True, 'language': 'zh', 'confidence': 0.9}
            elif re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
                return {'success': True, 'language': 'ja', 'confidence': 0.9}
            elif re.search(r'[\uac00-\ud7af]', text):
                return {'success': True, 'language': 'ko', 'confidence': 0.9}
            elif re.search(r'[\u0600-\u06ff]', text):
                return {'success': True, 'language': 'ar', 'confidence': 0.9}
            elif re.search(r'[\u0900-\u097f]', text):
                return {'success': True, 'language': 'hi', 'confidence': 0.8}
            else:
                # Default to English
                return {'success': True, 'language': 'en', 'confidence': 0.7}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

class LocalizationManager:
    """Manages localization for different regions and cultures."""
    
    def __init__(self, localization_dir: Path):
        self.localization_dir = localization_dir
        self.localization_data = self._load_localization_data()
    
    def _load_localization_data(self) -> Dict[str, Any]:
        """Load localization data for different regions."""
        # Placeholder for localization data
        return {
            'date_formats': {
                'en': 'MM/DD/YYYY',
                'de': 'DD.MM.YYYY',
                'fr': 'DD/MM/YYYY',
                'ja': 'YYYY/MM/DD'
            },
            'time_formats': {
                'en': '12-hour',
                'de': '24-hour',
                'fr': '24-hour',
                'ja': '24-hour'
            },
            'currency_formats': {
                'en': '$#,##0.00',
                'de': '#.##0,00 €',
                'fr': '#,##0.00 €',
                'ja': '¥#,##0'
            }
        }

class CulturalContextAdapter:
    """Adapts responses based on cultural context."""
    
    def adapt_response(self, response: str, target_culture: str) -> str:
        """Adapt response for cultural context."""
        # Placeholder for cultural adaptation
        # In real implementation, would adjust formality, expressions, etc.
        return response
