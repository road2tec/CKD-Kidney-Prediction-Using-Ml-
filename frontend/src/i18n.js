import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import base English translations
import enTranslation from './locales/en/translation.json';

// API base URL for translation service
const API_URL = 'http://localhost:5000/api';

// Supported languages configuration
export const SUPPORTED_LANGUAGES = {
    en: { name: 'English', native: 'English', flag: '🇺🇸', rtl: false },
    hi: { name: 'Hindi', native: 'हिंदी', flag: '🇮🇳', rtl: false },
    mr: { name: 'Marathi', native: 'मराठी', flag: '🇮🇳', rtl: false },
    ta: { name: 'Tamil', native: 'தமிழ்', flag: '🇮🇳', rtl: false },
    te: { name: 'Telugu', native: 'తెలుగు', flag: '🇮🇳', rtl: false },
    kn: { name: 'Kannada', native: 'ಕನ್ನಡ', flag: '🇮🇳', rtl: false },
    ml: { name: 'Malayalam', native: 'മലയാളം', flag: '🇮🇳', rtl: false },
    gu: { name: 'Gujarati', native: 'ગુજરાતી', flag: '🇮🇳', rtl: false },
    bn: { name: 'Bengali', native: 'বাংলা', flag: '🇮🇳', rtl: false },
    ur: { name: 'Urdu', native: 'اردو', flag: '🇵🇰', rtl: true }
};

// Base resources with pre-loaded translations (only English)
const resources = {
    en: { translation: enTranslation }
};

// Translation cache for dynamic translations
const translationCache = new Map();

// Load translations from backend API
const loadTranslationsFromAPI = async (langCode) => {
    try {
        // Check local cache first
        if (translationCache.has(langCode)) {
            return translationCache.get(langCode);
        }

        // For English, use the bundled translation
        if (langCode === 'en') {
            return enTranslation;
        }

        // For all other languages, request translation from backend
        // This includes Hindi, which will now be generated/fetched dynamically
        const response = await fetch(`${API_URL}/translate/translations/bundle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                bundle: enTranslation,
                target_lang: langCode
            })
        });

        if (!response.ok) {
            throw new Error(`Failed to load translations for ${langCode}`);
        }

        const data = await response.json();

        if (data.success && data.translations) {
            // Cache the translations
            translationCache.set(langCode, data.translations);
            return data.translations;
        }

        // Fallback to English
        return enTranslation;
    } catch (error) {
        console.error(`Error loading translations for ${langCode}:`, error);
        // Fallback to English
        return enTranslation;
    }
};

// Custom backend for loading translations dynamically
const translationBackend = {
    type: 'backend',
    read(language, namespace, callback) {
        loadTranslationsFromAPI(language)
            .then(translations => {
                callback(null, translations);
            })
            .catch(error => {
                callback(error, null);
            });
    }
};

// Initialize i18next with custom backend for dynamic translation loading
i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .use(translationBackend)  // Enable dynamic translation loading from backend
    .init({
        resources,
        fallbackLng: 'en',
        debug: false,

        // Don't load via backend for English (already bundled)
        partialBundledLanguages: true,

        interpolation: {
            escapeValue: false
        },

        detection: {
            order: ['localStorage', 'navigator'],
            caches: ['localStorage'],
            lookupLocalStorage: 'i18nextLng'
        },

        react: {
            useSuspense: false
        }
    });

// Function to dynamically load and add a language
export const loadLanguage = async (langCode) => {
    if (!SUPPORTED_LANGUAGES[langCode]) {
        console.warn(`Language ${langCode} is not supported`);
        return false;
    }

    try {
        // If language already loaded in resources
        if (i18n.hasResourceBundle(langCode, 'translation')) {
            return true;
        }

        // Load translations from API
        const translations = await loadTranslationsFromAPI(langCode);

        // Add to i18n resources
        i18n.addResourceBundle(langCode, 'translation', translations, true, true);

        return true;
    } catch (error) {
        console.error(`Failed to load language ${langCode}:`, error);
        return false;
    }
};

// Function to change language with dynamic loading
export const changeLanguage = async (langCode) => {
    if (!SUPPORTED_LANGUAGES[langCode]) {
        console.warn(`Language ${langCode} is not supported`);
        return false;
    }

    try {
        // Load the language if not already loaded
        await loadLanguage(langCode);

        // Change the language
        await i18n.changeLanguage(langCode);

        // Update document direction for RTL languages
        const isRTL = SUPPORTED_LANGUAGES[langCode].rtl;
        document.documentElement.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
        document.documentElement.setAttribute('lang', langCode);

        // Persist in localStorage
        localStorage.setItem('i18nextLng', langCode);

        return true;
    } catch (error) {
        console.error(`Failed to change language to ${langCode}:`, error);
        return false;
    }
};

// Function to translate dynamic content (API responses, etc.)
export const translateDynamic = async (text, targetLang = null) => {
    const lang = targetLang || i18n.language;

    if (lang === 'en') {
        return text;
    }

    try {
        const response = await fetch(`${API_URL}/translate/translate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text,
                target_lang: lang,
                source_lang: 'en'
            })
        });

        if (!response.ok) {
            return text;
        }

        const data = await response.json();
        return data.success ? data.translation : text;
    } catch (error) {
        console.error('Translation error:', error);
        return text;
    }
};

// Function to translate batch of texts
export const translateBatch = async (texts, targetLang = null) => {
    const lang = targetLang || i18n.language;

    if (lang === 'en') {
        return texts;
    }

    try {
        const response = await fetch(`${API_URL}/translate/translate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: texts,
                target_lang: lang,
                source_lang: 'en'
            })
        });

        if (!response.ok) {
            return texts;
        }

        const data = await response.json();
        return data.success ? data.translation : texts;
    } catch (error) {
        console.error('Batch translation error:', error);
        return texts;
    }
};

// Function to translate object (API response)
export const translateObject = async (obj, targetLang = null, keysToTranslate = null) => {
    const lang = targetLang || i18n.language;

    if (lang === 'en') {
        return obj;
    }

    try {
        const response = await fetch(`${API_URL}/translate/translate/object`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                object: obj,
                target_lang: lang,
                source_lang: 'en',
                keys_to_translate: keysToTranslate
            })
        });

        if (!response.ok) {
            return obj;
        }

        const data = await response.json();
        return data.success ? data.translated_object : obj;
    } catch (error) {
        console.error('Object translation error:', error);
        return obj;
    }
};

// Get current language info
export const getCurrentLanguage = () => {
    const code = i18n.language || 'en';
    return {
        code,
        ...SUPPORTED_LANGUAGES[code]
    };
};

// Get all supported languages
export const getSupportedLanguages = () => {
    return Object.entries(SUPPORTED_LANGUAGES).map(([code, info]) => ({
        code,
        ...info
    }));
};

export default i18n;
