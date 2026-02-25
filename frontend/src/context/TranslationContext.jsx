import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
    translateDynamic,
    translateBatch,
    translateObject,
    SUPPORTED_LANGUAGES
} from '../i18n';

// Translation Context
const TranslationContext = createContext(null);

/**
 * Translation Provider - Provides translation utilities to the entire app
 */
export const TranslationProvider = ({ children }) => {
    const { i18n, t } = useTranslation();
    const [isTranslating, setIsTranslating] = useState(false);
    const [translationCache, setTranslationCache] = useState(new Map());

    // Listen for language changes
    useEffect(() => {
        const handleLanguageChange = () => {
            // Clear cache on language change
            setTranslationCache(new Map());
        };

        i18n.on('languageChanged', handleLanguageChange);
        window.addEventListener('languageChanged', handleLanguageChange);

        return () => {
            i18n.off('languageChanged', handleLanguageChange);
            window.removeEventListener('languageChanged', handleLanguageChange);
        };
    }, [i18n]);

    // Translate a single text dynamically
    const translate = useCallback(async (text, options = {}) => {
        if (!text) return text;

        const targetLang = options.targetLang || i18n.language;

        // Check if translation exists in static bundle
        if (options.key) {
            const staticTranslation = t(options.key, { defaultValue: null });
            if (staticTranslation) return staticTranslation;
        }

        // Check cache
        const cacheKey = `${targetLang}:${text}`;
        if (translationCache.has(cacheKey)) {
            return translationCache.get(cacheKey);
        }

        // If target language is English, return original
        if (targetLang === 'en') return text;

        try {
            setIsTranslating(true);
            const translated = await translateDynamic(text, targetLang);

            // Update cache
            setTranslationCache(prev => new Map(prev).set(cacheKey, translated));

            return translated;
        } catch (error) {
            console.error('Translation error:', error);
            return text;
        } finally {
            setIsTranslating(false);
        }
    }, [i18n.language, t, translationCache]);

    // Translate multiple texts at once
    const translateMany = useCallback(async (texts, options = {}) => {
        if (!texts || texts.length === 0) return texts;

        const targetLang = options.targetLang || i18n.language;

        // If target language is English, return original
        if (targetLang === 'en') return texts;

        // Check cache for each text
        const results = new Array(texts.length);
        const uncachedTexts = [];
        const uncachedIndices = [];

        texts.forEach((text, index) => {
            const cacheKey = `${targetLang}:${text}`;
            if (translationCache.has(cacheKey)) {
                results[index] = translationCache.get(cacheKey);
            } else {
                uncachedTexts.push(text);
                uncachedIndices.push(index);
            }
        });

        // If all texts are cached, return results
        if (uncachedTexts.length === 0) return results;

        try {
            setIsTranslating(true);
            const translated = await translateBatch(uncachedTexts, targetLang);

            // Update results and cache
            const newCache = new Map(translationCache);
            translated.forEach((trans, i) => {
                const originalIndex = uncachedIndices[i];
                results[originalIndex] = trans;
                newCache.set(`${targetLang}:${uncachedTexts[i]}`, trans);
            });
            setTranslationCache(newCache);

            return results;
        } catch (error) {
            console.error('Batch translation error:', error);
            // Return original texts for failed translations
            uncachedIndices.forEach((index, i) => {
                results[index] = uncachedTexts[i];
            });
            return results;
        } finally {
            setIsTranslating(false);
        }
    }, [i18n.language, translationCache]);

    // Translate an object (e.g., API response)
    const translateResponse = useCallback(async (obj, options = {}) => {
        if (!obj) return obj;

        const targetLang = options.targetLang || i18n.language;

        // If target language is English, return original
        if (targetLang === 'en') return obj;

        try {
            setIsTranslating(true);
            return await translateObject(obj, targetLang, options.keys);
        } catch (error) {
            console.error('Object translation error:', error);
            return obj;
        } finally {
            setIsTranslating(false);
        }
    }, [i18n.language]);

    // Get language info
    const getLanguageInfo = useCallback((langCode = null) => {
        const code = langCode || i18n.language;
        return SUPPORTED_LANGUAGES[code] || SUPPORTED_LANGUAGES['en'];
    }, [i18n.language]);

    // Check if current language is RTL
    const isRTL = useCallback(() => {
        return getLanguageInfo().rtl === true;
    }, [getLanguageInfo]);

    const value = {
        // Current language info
        language: i18n.language,
        languageInfo: getLanguageInfo(),
        isRTL: isRTL(),
        supportedLanguages: SUPPORTED_LANGUAGES,

        // Translation functions
        t, // Standard i18next t function for static translations
        translate, // Translate single dynamic text
        translateMany, // Translate multiple texts
        translateResponse, // Translate API response object

        // State
        isTranslating,

        // Utilities
        getLanguageInfo
    };

    return (
        <TranslationContext.Provider value={value}>
            {children}
        </TranslationContext.Provider>
    );
};

/**
 * Hook to use translation context
 */
export const useAppTranslation = () => {
    const context = useContext(TranslationContext);
    if (!context) {
        throw new Error('useAppTranslation must be used within a TranslationProvider');
    }
    return context;
};

/**
 * Component that translates its children or text prop dynamically
 * Supports both: <DynamicText text="hello" /> and <DynamicText>hello</DynamicText>
 */
export const DynamicText = ({ children, text, fallback = null }) => {
    const content = text !== undefined ? text : children;
    const { translate, language } = useAppTranslation();
    const [translated, setTranslated] = useState(content);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (content === null || content === undefined) {
            setTranslated('');
            return;
        }

        if (typeof content !== 'string') {
            setTranslated(content);
            return;
        }

        if (language === 'en') {
            setTranslated(content);
            return;
        }

        let mounted = true;
        setLoading(true);

        translate(content).then(result => {
            if (mounted) {
                setTranslated(result);
                setLoading(false);
            }
        }).catch(() => {
            if (mounted) {
                setTranslated(content);
                setLoading(false);
            }
        });

        return () => {
            mounted = false;
        };
    }, [content, translate, language]);

    if (loading && fallback) {
        return fallback;
    }

    return translated || '';
};

/**
 * Higher-order component to provide translation props
 */
export const withTranslation = (WrappedComponent) => {
    return function WithTranslationComponent(props) {
        const translationContext = useAppTranslation();
        return <WrappedComponent {...props} {...translationContext} />;
    };
};

export default TranslationContext;
