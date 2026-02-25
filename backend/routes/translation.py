"""
Translation API Routes - REST endpoints for translation services
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
import os
import json

from services.translation_service import (
    get_translation_service, 
    SUPPORTED_LANGUAGES,
    DEFAULT_TRANSLATIONS
)
from config import MONGO_URI, DATABASE_NAME

# Initialize MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Create blueprint
translation_bp = Blueprint('translation', __name__)


@translation_bp.route('/translate', methods=['POST'])
def translate_text():
    """
    Translate text from source to target language
    
    Request body:
    {
        "text": "Text to translate" | ["Text 1", "Text 2", ...],
        "target_lang": "hi",
        "source_lang": "en" (optional, default: "en")
    }
    
    Response:
    {
        "success": true,
        "translation": "Translated text" | ["Translation 1", "Translation 2", ...],
        "source_lang": "en",
        "target_lang": "hi"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        text = data.get('text')
        target_lang = data.get('target_lang', 'en')
        source_lang = data.get('source_lang', 'en')
        
        if not text:
            return jsonify({
                'success': False,
                'message': 'Text is required'
            }), 400
        
        if target_lang not in SUPPORTED_LANGUAGES:
            return jsonify({
                'success': False,
                'message': f'Unsupported target language: {target_lang}',
                'supported_languages': list(SUPPORTED_LANGUAGES.keys())
            }), 400
        
        service = get_translation_service(db)
        
        # Handle batch translation
        if isinstance(text, list):
            translations = service.translate_batch(text, target_lang, source_lang)
            return jsonify({
                'success': True,
                'translation': translations,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'count': len(translations)
            })
        else:
            translation = service.translate_text(text, target_lang, source_lang)
            return jsonify({
                'success': True,
                'translation': translation,
                'source_lang': source_lang,
                'target_lang': target_lang
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Translation failed: {str(e)}'
        }), 500


@translation_bp.route('/translate/object', methods=['POST'])
def translate_object():
    """
    Translate all string values in a JSON object
    
    Request body:
    {
        "object": { "key1": "value1", "nested": { "key2": "value2" } },
        "target_lang": "hi",
        "source_lang": "en" (optional),
        "keys_to_translate": ["key1", "key2"] (optional, translates all if not provided)
    }
    
    Response:
    {
        "success": true,
        "translated_object": { ... },
        "source_lang": "en",
        "target_lang": "hi"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        obj = data.get('object')
        target_lang = data.get('target_lang', 'en')
        source_lang = data.get('source_lang', 'en')
        keys_to_translate = data.get('keys_to_translate')
        
        if not obj:
            return jsonify({
                'success': False,
                'message': 'Object is required'
            }), 400
        
        if target_lang not in SUPPORTED_LANGUAGES:
            return jsonify({
                'success': False,
                'message': f'Unsupported target language: {target_lang}'
            }), 400
        
        service = get_translation_service(db)
        translated = service.translate_object(obj, target_lang, source_lang, keys_to_translate)
        
        return jsonify({
            'success': True,
            'translated_object': translated,
            'source_lang': source_lang,
            'target_lang': target_lang
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Translation failed: {str(e)}'
        }), 500


@translation_bp.route('/languages', methods=['GET'])
def get_languages():
    """
    Get list of supported languages
    
    Response:
    {
        "success": true,
        "languages": {
            "en": { "name": "English", "native": "English", "flag": "🇺🇸", "rtl": false },
            ...
        }
    }
    """
    return jsonify({
        'success': True,
        'languages': SUPPORTED_LANGUAGES,
        'default_language': 'en',
        'count': len(SUPPORTED_LANGUAGES)
    })


@translation_bp.route('/translations/<lang_code>', methods=['GET'])
def get_translations(lang_code):
    """
    Get all cached/default translations for a specific language
    This is used to get the complete translation bundle for the frontend
    
    Response:
    {
        "success": true,
        "language": "hi",
        "translations": { ... },
        "rtl": false
    }
    """
    if lang_code not in SUPPORTED_LANGUAGES:
        return jsonify({
            'success': False,
            'message': f'Unsupported language: {lang_code}'
        }), 400
    
    # Get default translations for this language
    translations = DEFAULT_TRANSLATIONS.get(lang_code, {})
    
    return jsonify({
        'success': True,
        'language': lang_code,
        'language_info': SUPPORTED_LANGUAGES[lang_code],
        'translations': translations,
        'rtl': SUPPORTED_LANGUAGES[lang_code].get('rtl', False)
    })


@translation_bp.route('/translations/bundle', methods=['POST'])
def get_translation_bundle():
    """
    Get translations for a complete bundle (like a full translation.json file)
    Translates the English bundle to the requested language
    
    Request body:
    {
        "bundle": { ... English translations ... },
        "target_lang": "hi"
    }
    
    Response:
    {
        "success": true,
        "translations": { ... translated bundle ... },
        "target_lang": "hi"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        bundle = data.get('bundle')
        target_lang = data.get('target_lang', 'en')
        
        if not bundle:
            return jsonify({
                'success': False,
                'message': 'Bundle is required'
            }), 400
        
        if target_lang not in SUPPORTED_LANGUAGES:
            return jsonify({
                'success': False,
                'message': f'Unsupported language: {target_lang}'
            }), 400
        
        # If target is English, return the bundle as-is
        if target_lang == 'en':
            return jsonify({
                'success': True,
                'translations': bundle,
                'target_lang': target_lang
            })
        
        service = get_translation_service(db)
        translated_bundle = service.translate_object(bundle, target_lang, 'en')
        
        return jsonify({
            'success': True,
            'translations': translated_bundle,
            'target_lang': target_lang,
            'language_info': SUPPORTED_LANGUAGES[target_lang]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Translation failed: {str(e)}'
        }), 500


@translation_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """
    Get translation service statistics (admin only)
    
    Response:
    {
        "success": true,
        "stats": { ... }
    }
    """
    try:
        identity = get_jwt_identity()
        user_data = json.loads(identity) if isinstance(identity, str) else identity
        
        if user_data.get('role') != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
        
        service = get_translation_service(db)
        stats = service.get_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get stats: {str(e)}'
        }), 500


@translation_bp.route('/cache/clear', methods=['POST'])
@jwt_required()
def clear_cache():
    """
    Clear translation cache (admin only)
    
    Response:
    {
        "success": true,
        "message": "Cache cleared successfully"
    }
    """
    try:
        identity = get_jwt_identity()
        user_data = json.loads(identity) if isinstance(identity, str) else identity
        
        if user_data.get('role') != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
        
        service = get_translation_service(db)
        service.memory_cache.clear()
        
        return jsonify({
            'success': True,
            'message': 'Memory cache cleared successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to clear cache: {str(e)}'
        }), 500
