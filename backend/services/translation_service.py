"""
Translation Service - Google Translate API Integration with Caching
Provides secure translation services for the CKD Prediction System
"""

import hashlib
import json
import os
import time
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional, Tuple
import requests
from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Translate API configuration
GOOGLE_TRANSLATE_API_KEY = os.environ.get('GOOGLE_TRANSLATE_API_KEY', 'AIzaSyCWQfokomdKcDKln2gWRczUTEoTa7y0IsE')
GOOGLE_TRANSLATE_URL = "https://translation.googleapis.com/language/translate/v2"

# Supported languages with their codes and native names
SUPPORTED_LANGUAGES = {
    'en': {'name': 'English', 'native': 'English', 'flag': '🇺🇸', 'rtl': False},
    'hi': {'name': 'Hindi', 'native': 'हिंदी', 'flag': '🇮🇳', 'rtl': False},
    'mr': {'name': 'Marathi', 'native': 'मराठी', 'flag': '🇮🇳', 'rtl': False},
    'ta': {'name': 'Tamil', 'native': 'தமிழ்', 'flag': '🇮🇳', 'rtl': False},
    'te': {'name': 'Telugu', 'native': 'తెలుగు', 'flag': '🇮🇳', 'rtl': False},
    'kn': {'name': 'Kannada', 'native': 'ಕನ್ನಡ', 'flag': '🇮🇳', 'rtl': False},
    'ml': {'name': 'Malayalam', 'native': 'മലയാളം', 'flag': '🇮🇳', 'rtl': False},
    'gu': {'name': 'Gujarati', 'native': 'ગુજરાતી', 'flag': '🇮🇳', 'rtl': False},
    'bn': {'name': 'Bengali', 'native': 'বাংলা', 'flag': '🇮🇳', 'rtl': False},
    'ur': {'name': 'Urdu', 'native': 'اردو', 'flag': '🇵🇰', 'rtl': True}
}

class InMemoryCache:
    """Simple in-memory cache with expiration"""
    
    def __init__(self, max_size: int = 10000, ttl_seconds: int = 86400):
        self._cache: Dict[str, Tuple[str, float]] = {}
        self._max_size = max_size
        self._ttl = ttl_seconds
    
    def _generate_key(self, text: str, target_lang: str, source_lang: str = 'en') -> str:
        """Generate a unique cache key"""
        content = f"{source_lang}:{target_lang}:{text}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get(self, text: str, target_lang: str, source_lang: str = 'en') -> Optional[str]:
        """Get cached translation"""
        key = self._generate_key(text, target_lang, source_lang)
        if key in self._cache:
            translation, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return translation
            else:
                del self._cache[key]
        return None
    
    def set(self, text: str, translation: str, target_lang: str, source_lang: str = 'en'):
        """Store translation in cache"""
        # Evict old entries if cache is full
        if len(self._cache) >= self._max_size:
            # Remove oldest 10% of entries
            entries = sorted(self._cache.items(), key=lambda x: x[1][1])
            for key, _ in entries[:int(self._max_size * 0.1)]:
                del self._cache[key]
        
        key = self._generate_key(text, target_lang, source_lang)
        self._cache[key] = (translation, time.time())
    
    def clear(self):
        """Clear cache"""
        self._cache.clear()
    
    def stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'size': len(self._cache),
            'max_size': self._max_size,
            'ttl_seconds': self._ttl
        }


class MongoDBCache:
    """MongoDB-based persistent cache for translations"""
    
    def __init__(self, db, ttl_days: int = 30):
        self.collection = db.translations_cache
        self._ttl = ttl_days
        # Create indexes
        self.collection.create_index('cache_key', unique=True)
        self.collection.create_index('created_at', expireAfterSeconds=ttl_days * 86400)
    
    def _generate_key(self, text: str, target_lang: str, source_lang: str = 'en') -> str:
        """Generate a unique cache key"""
        content = f"{source_lang}:{target_lang}:{text}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get(self, text: str, target_lang: str, source_lang: str = 'en') -> Optional[str]:
        """Get cached translation from MongoDB"""
        key = self._generate_key(text, target_lang, source_lang)
        doc = self.collection.find_one({'cache_key': key})
        if doc:
            return doc.get('translation')
        return None
    
    def set(self, text: str, translation: str, target_lang: str, source_lang: str = 'en'):
        """Store translation in MongoDB cache"""
        key = self._generate_key(text, target_lang, source_lang)
        self.collection.update_one(
            {'cache_key': key},
            {
                '$set': {
                    'source_text': text,
                    'translation': translation,
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'created_at': datetime.utcnow()
                }
            },
            upsert=True
        )
    
    def get_batch(self, texts: List[str], target_lang: str, source_lang: str = 'en') -> Dict[str, str]:
        """Get multiple cached translations"""
        keys = [self._generate_key(text, target_lang, source_lang) for text in texts]
        docs = self.collection.find({'cache_key': {'$in': keys}})
        
        result = {}
        for doc in docs:
            result[doc['source_text']] = doc['translation']
        return result
    
    def set_batch(self, translations: Dict[str, str], target_lang: str, source_lang: str = 'en'):
        """Store multiple translations"""
        for text, translation in translations.items():
            self.set(text, translation, target_lang, source_lang)
    
    def stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'total_entries': self.collection.count_documents({}),
            'ttl_days': self._ttl
        }


class TranslationService:
    """Main translation service with Google Translate API and caching"""
    
    def __init__(self, db=None):
        self.api_key = GOOGLE_TRANSLATE_API_KEY
        self.api_url = GOOGLE_TRANSLATE_URL
        
        # Initialize caches
        self.memory_cache = InMemoryCache(max_size=5000, ttl_seconds=3600)  # 1 hour in memory
        self.db_cache = MongoDBCache(db) if db is not None else None
        
        # Statistics
        self.stats = {
            'api_calls': 0,
            'cache_hits_memory': 0,
            'cache_hits_db': 0,
            'cache_misses': 0
        }
    
    def translate_text(self, text: str, target_lang: str, source_lang: str = 'en') -> str:
        """
        Translate a single text string
        
        Args:
            text: Text to translate
            target_lang: Target language code (e.g., 'hi', 'mr')
            source_lang: Source language code (default: 'en')
        
        Returns:
            Translated text string
        """
        if not text or not text.strip():
            return text
        
        # Don't translate if target is same as source
        if target_lang == source_lang:
            return text
        
        # Check if language is supported
        if target_lang not in SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported target language: {target_lang}")
            return text
        
        # Check memory cache first
        cached = self.memory_cache.get(text, target_lang, source_lang)
        if cached:
            self.stats['cache_hits_memory'] += 1
            return cached
        
        # Check MongoDB cache
        if self.db_cache:
            cached = self.db_cache.get(text, target_lang, source_lang)
            if cached:
                self.stats['cache_hits_db'] += 1
                # Also store in memory cache for faster access
                self.memory_cache.set(text, cached, target_lang, source_lang)
                return cached
        
        self.stats['cache_misses'] += 1
        
        # Call Google Translate API
        try:
            translation = self._call_google_translate(text, target_lang, source_lang)
            
            # Store in caches
            self.memory_cache.set(text, translation, target_lang, source_lang)
            if self.db_cache:
                self.db_cache.set(text, translation, target_lang, source_lang)
            
            return translation
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return text  # Return original text on failure
    
    def translate_batch(self, texts: List[str], target_lang: str, source_lang: str = 'en') -> List[str]:
        """
        Translate multiple texts at once (more efficient for API calls)
        
        Args:
            texts: List of texts to translate
            target_lang: Target language code
            source_lang: Source language code
        
        Returns:
            List of translated texts
        """
        if not texts:
            return []
        
        if target_lang == source_lang:
            return texts
        
        results = {}
        texts_to_translate = []
        
        # Check caches for each text
        for text in texts:
            if not text or not text.strip():
                results[text] = text
                continue
            
            cached = self.memory_cache.get(text, target_lang, source_lang)
            if cached:
                results[text] = cached
                self.stats['cache_hits_memory'] += 1
                continue
            
            if self.db_cache:
                cached = self.db_cache.get(text, target_lang, source_lang)
                if cached:
                    results[text] = cached
                    self.stats['cache_hits_db'] += 1
                    self.memory_cache.set(text, cached, target_lang, source_lang)
                    continue
            
            texts_to_translate.append(text)
        
        # Batch translate uncached texts
        if texts_to_translate:
            self.stats['cache_misses'] += len(texts_to_translate)
            try:
                # Google Translate supports batch requests
                translations = self._call_google_translate_batch(texts_to_translate, target_lang, source_lang)
                
                for orig, trans in zip(texts_to_translate, translations):
                    results[orig] = trans
                    self.memory_cache.set(orig, trans, target_lang, source_lang)
                    if self.db_cache:
                        self.db_cache.set(orig, trans, target_lang, source_lang)
            except Exception as e:
                logger.error(f"Batch translation failed: {str(e)}")
                for text in texts_to_translate:
                    results[text] = text
        
        # Return in original order
        return [results.get(text, text) for text in texts]
    
    def translate_object(self, obj: Dict, target_lang: str, source_lang: str = 'en', keys_to_translate: List[str] = None) -> Dict:
        """
        Translate all string values in a dictionary/object
        
        Args:
            obj: Dictionary to translate
            target_lang: Target language code
            source_lang: Source language code
            keys_to_translate: Optional list of specific keys to translate (translates all if None)
        
        Returns:
            Translated dictionary
        """
        if not obj or target_lang == source_lang:
            return obj
        
        def extract_strings(d, prefix=''):
            """Extract all translatable strings from nested dict"""
            strings = {}
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, str):
                    if keys_to_translate is None or key in keys_to_translate:
                        strings[full_key] = value
                elif isinstance(value, dict):
                    strings.update(extract_strings(value, full_key))
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, str):
                            strings[f"{full_key}[{i}]"] = item
                        elif isinstance(item, dict):
                            strings.update(extract_strings(item, f"{full_key}[{i}]"))
            return strings
        
        def inject_translations(d, translations, prefix=''):
            """Inject translations back into nested dict"""
            result = {}
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, str):
                    result[key] = translations.get(full_key, value)
                elif isinstance(value, dict):
                    result[key] = inject_translations(value, translations, full_key)
                elif isinstance(value, list):
                    new_list = []
                    for i, item in enumerate(value):
                        if isinstance(item, str):
                            new_list.append(translations.get(f"{full_key}[{i}]", item))
                        elif isinstance(item, dict):
                            new_list.append(inject_translations(item, translations, f"{full_key}[{i}]"))
                        else:
                            new_list.append(item)
                    result[key] = new_list
                else:
                    result[key] = value
            return result
        
        # Extract strings
        strings = extract_strings(obj)
        if not strings:
            return obj
        
        # Batch translate
        keys = list(strings.keys())
        values = list(strings.values())
        translated_values = self.translate_batch(values, target_lang, source_lang)
        
        # Create translation map
        translations = dict(zip(keys, translated_values))
        
        # Inject back
        return inject_translations(obj, translations)
    
    def _call_google_translate(self, text: str, target_lang: str, source_lang: str = 'en') -> str:
        """Make a single translation API call"""
        self.stats['api_calls'] += 1
        
        params = {
            'key': self.api_key,
            'q': text,
            'target': target_lang,
            'source': source_lang,
            'format': 'text'
        }
        
        response = requests.post(self.api_url, data=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if 'data' in data and 'translations' in data['data']:
            return data['data']['translations'][0]['translatedText']
        
        return text
    
    def _call_google_translate_batch(self, texts: List[str], target_lang: str, source_lang: str = 'en') -> List[str]:
        """Make a batch translation API call using POST to avoid URL length limits"""
        self.stats['api_calls'] += 1
        
        # Google Translate can handle up to 128 texts per request, but we'll use smaller batches for reliability
        batch_size = 50
        all_translations = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                # Use POST request with form data - this avoids URL length limits
                # The 'q' parameter can be repeated for multiple texts
                form_data = [
                    ('key', self.api_key),
                    ('target', target_lang),
                    ('source', source_lang),
                    ('format', 'text')
                ]
                
                # Add each text as a separate 'q' parameter
                for text in batch:
                    form_data.append(('q', text))
                
                response = requests.post(self.api_url, data=form_data, timeout=60)
                
                if response.status_code != 200:
                    logger.error(f"Google Translate API error: {response.status_code} - {response.text}")
                    # On error, return original texts for this batch
                    all_translations.extend(batch)
                    continue
                
                result = response.json()
                
                if 'error' in result:
                    logger.error(f"Google Translate API error: {result['error']}")
                    all_translations.extend(batch)
                    continue
                
                if 'data' in result and 'translations' in result['data']:
                    all_translations.extend([t['translatedText'] for t in result['data']['translations']])
                else:
                    logger.warning(f"Unexpected response format from Google Translate API")
                    all_translations.extend(batch)
                    
            except requests.exceptions.Timeout:
                logger.error(f"Google Translate API timeout for batch starting at index {i}")
                all_translations.extend(batch)
            except requests.exceptions.RequestException as e:
                logger.error(f"Google Translate API request failed: {str(e)}")
                all_translations.extend(batch)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Google Translate API response: {str(e)}")
                all_translations.extend(batch)
            except Exception as e:
                logger.error(f"Unexpected error during batch translation: {str(e)}")
                all_translations.extend(batch)
        
        return all_translations
    
    def get_supported_languages(self) -> Dict:
        """Get list of supported languages"""
        return SUPPORTED_LANGUAGES
    
    def get_stats(self) -> Dict:
        """Get translation service statistics"""
        return {
            **self.stats,
            'memory_cache': self.memory_cache.stats(),
            'db_cache': self.db_cache.stats() if self.db_cache else None
        }


# Default translations for common UI elements (pre-translated to avoid API calls)
DEFAULT_TRANSLATIONS = {
    'hi': {
        'welcome': 'स्वागत है',
        'login': 'लॉगिन',
        'logout': 'लॉगआउट',
        'register': 'पंजीकरण करें',
        'dashboard': 'डैशबोर्ड',
        'profile': 'प्रोफ़ाइल',
        'settings': 'सेटिंग्स',
        'submit': 'जमा करें',
        'cancel': 'रद्द करें',
        'save': 'सहेजें',
        'delete': 'हटाएं',
        'edit': 'संपादित करें',
        'loading': 'लोड हो रहा है...',
        'error': 'त्रुटि',
        'success': 'सफलता'
    },
    'mr': {
        'welcome': 'स्वागत आहे',
        'login': 'लॉगिन',
        'logout': 'लॉगआउट',
        'register': 'नोंदणी करा',
        'dashboard': 'डॅशबोर्ड',
        'profile': 'प्रोफाइल',
        'settings': 'सेटिंग्ज',
        'submit': 'सबमिट करा',
        'cancel': 'रद्द करा',
        'save': 'जतन करा',
        'delete': 'हटवा',
        'edit': 'संपादित करा',
        'loading': 'लोड होत आहे...',
        'error': 'त्रुटी',
        'success': 'यशस्वी'
    },
    'ta': {
        'welcome': 'வரவேற்கிறோம்',
        'login': 'உள்நுழைவு',
        'logout': 'வெளியேறு',
        'register': 'பதிவு செய்யுங்கள்',
        'dashboard': 'டாஷ்போர்டு',
        'profile': 'சுயவிவரம்',
        'settings': 'அமைப்புகள்',
        'submit': 'சமர்ப்பிக்கவும்',
        'cancel': 'ரத்துசெய்',
        'save': 'சேமி',
        'delete': 'நீக்கு',
        'edit': 'திருத்து',
        'loading': 'ஏற்றுகிறது...',
        'error': 'பிழை',
        'success': 'வெற்றி'
    },
    'te': {
        'welcome': 'స్వాగతం',
        'login': 'లాగిన్',
        'logout': 'లాగ్ అవుట్',
        'register': 'నమోదు చేయండి',
        'dashboard': 'డాష్‌బోర్డ్',
        'profile': 'ప్రొఫైల్',
        'settings': 'సెట్టింగ్‌లు',
        'submit': 'సమర్పించండి',
        'cancel': 'రద్దు చేయండి',
        'save': 'సేవ్ చేయండి',
        'delete': 'తొలగించు',
        'edit': 'సవరించు',
        'loading': 'లోడ్ అవుతోంది...',
        'error': 'దోషం',
        'success': 'విజయం'
    },
    'kn': {
        'welcome': 'ಸ್ವಾಗತ',
        'login': 'ಲಾಗಿನ್',
        'logout': 'ಲಾಗ್ ಔಟ್',
        'register': 'ನೋಂದಣಿ',
        'dashboard': 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
        'profile': 'ಪ್ರೊಫೈಲ್',
        'settings': 'ಸೆಟ್ಟಿಂಗ್‌ಗಳು',
        'submit': 'ಸಲ್ಲಿಸಿ',
        'cancel': 'ರದ್ದುಮಾಡಿ',
        'save': 'ಉಳಿಸಿ',
        'delete': 'ಅಳಿಸು',
        'edit': 'ಸಂಪಾದಿಸು',
        'loading': 'ಲೋಡ್ ಆಗುತ್ತಿದೆ...',
        'error': 'ದೋಷ',
        'success': 'ಯಶಸ್ಸು'
    },
    'ml': {
        'welcome': 'സ്വാഗതം',
        'login': 'ലോഗിൻ',
        'logout': 'ലോഗൗട്ട്',
        'register': 'രജിസ്റ്റർ ചെയ്യുക',
        'dashboard': 'ഡാഷ്ബോർഡ്',
        'profile': 'പ്രൊഫൈൽ',
        'settings': 'ക്രമീകരണങ്ങൾ',
        'submit': 'സമർപ്പിക്കുക',
        'cancel': 'റദ്ദാക്കുക',
        'save': 'സേവ് ചെയ്യുക',
        'delete': 'ഇല്ലാതാക്കുക',
        'edit': 'എഡിറ്റ് ചെയ്യുക',
        'loading': 'ലോഡ് ചെയ്യുന്നു...',
        'error': 'പിശക്',
        'success': 'വിജയം'
    },
    'gu': {
        'welcome': 'સ્વાગત છે',
        'login': 'લૉગિન',
        'logout': 'લૉગ આઉટ',
        'register': 'નોંધણી કરો',
        'dashboard': 'ડેશબોર્ડ',
        'profile': 'પ્રોફાઇલ',
        'settings': 'સેટિંગ્સ',
        'submit': 'સબમિટ કરો',
        'cancel': 'રદ કરો',
        'save': 'સાચવો',
        'delete': 'કાઢી નાખો',
        'edit': 'સંપાદિત કરો',
        'loading': 'લોડ થઈ રહ્યું છે...',
        'error': 'ભૂલ',
        'success': 'સફળતા'
    },
    'bn': {
        'welcome': 'স্বাগতম',
        'login': 'লগইন',
        'logout': 'লগ আউট',
        'register': 'নিবন্ধন করুন',
        'dashboard': 'ড্যাশবোর্ড',
        'profile': 'প্রোফাইল',
        'settings': 'সেটিংস',
        'submit': 'জমা দিন',
        'cancel': 'বাতিল করুন',
        'save': 'সংরক্ষণ করুন',
        'delete': 'মুছে ফেলুন',
        'edit': 'সম্পাদনা করুন',
        'loading': 'লোড হচ্ছে...',
        'error': 'ত্রুটি',
        'success': 'সাফল্য'
    },
    'ur': {
        'welcome': 'خوش آمدید',
        'login': 'لاگ ان',
        'logout': 'لاگ آؤٹ',
        'register': 'رجسٹر کریں',
        'dashboard': 'ڈیش بورڈ',
        'profile': 'پروفائل',
        'settings': 'ترتیبات',
        'submit': 'جمع کریں',
        'cancel': 'منسوخ کریں',
        'save': 'محفوظ کریں',
        'delete': 'حذف کریں',
        'edit': 'ترمیم کریں',
        'loading': 'لوڈ ہو رہا ہے...',
        'error': 'خرابی',
        'success': 'کامیابی'
    }
}


# Singleton instance
_translation_service: Optional[TranslationService] = None

def get_translation_service(db=None) -> TranslationService:
    """Get or create the translation service singleton"""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService(db)
    return _translation_service
