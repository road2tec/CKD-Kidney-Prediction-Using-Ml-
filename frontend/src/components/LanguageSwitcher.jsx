import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { FaGlobe, FaChevronDown, FaCheck, FaSpinner } from 'react-icons/fa';
import { changeLanguage, SUPPORTED_LANGUAGES, getCurrentLanguage } from '../i18n';
import './LanguageSwitcher.css';

// Convert SUPPORTED_LANGUAGES object to array for easier mapping
const languages = Object.entries(SUPPORTED_LANGUAGES).map(([code, info]) => ({
    code,
    ...info
}));

const LanguageSwitcher = ({ variant = 'default' }) => {
    const { i18n, t } = useTranslation();
    const [isOpen, setIsOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [loadingLang, setLoadingLang] = useState(null);
    const dropdownRef = useRef(null);

    const currentLang = languages.find(lang => lang.code === i18n.language) || languages[0];

    const handleChangeLanguage = async (langCode) => {
        if (langCode === i18n.language) {
            setIsOpen(false);
            return;
        }

        setIsLoading(true);
        setLoadingLang(langCode);

        try {
            const success = await changeLanguage(langCode);
            if (success) {
                // Force re-render of the app
                window.dispatchEvent(new Event('languageChanged'));
            }
        } catch (error) {
            console.error('Failed to change language:', error);
        } finally {
            setIsLoading(false);
            setLoadingLang(null);
            setIsOpen(false);
        }
    };

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // Handle keyboard navigation
    useEffect(() => {
        const handleKeyDown = (event) => {
            if (!isOpen) return;

            if (event.key === 'Escape') {
                setIsOpen(false);
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [isOpen]);

    return (
        <div className={`language-switcher ${variant}`} ref={dropdownRef}>
            <button
                className={`language-btn ${isOpen ? 'open' : ''}`}
                onClick={() => setIsOpen(!isOpen)}
                aria-label={t('language.select', 'Select Language')}
                aria-expanded={isOpen}
                aria-haspopup="listbox"
                disabled={isLoading}
            >
                <FaGlobe className="globe-icon" />
                <span className="current-lang">
                    <span className="lang-flag">{currentLang.flag}</span>
                    <span className="lang-name-short">{currentLang.code.toUpperCase()}</span>
                    <span className="lang-name-full">{currentLang.native}</span>
                </span>
                {isLoading ? (
                    <FaSpinner className="chevron spinning" />
                ) : (
                    <FaChevronDown className={`chevron ${isOpen ? 'open' : ''}`} />
                )}
            </button>

            {isOpen && (
                <div className="language-dropdown" role="listbox">
                    <div className="dropdown-header">
                        <span>{t('language.select', 'Select Language')}</span>
                    </div>
                    <div className="languages-grid">
                        {languages.map(lang => (
                            <button
                                key={lang.code}
                                className={`language-option ${lang.code === i18n.language ? 'active' : ''} ${loadingLang === lang.code ? 'loading' : ''}`}
                                onClick={() => handleChangeLanguage(lang.code)}
                                role="option"
                                aria-selected={lang.code === i18n.language}
                                disabled={isLoading}
                            >
                                <span className="lang-flag">{lang.flag}</span>
                                <div className="lang-info">
                                    <span className="lang-native">{lang.native}</span>
                                    <span className="lang-english">{lang.name}</span>
                                </div>
                                {lang.code === i18n.language && (
                                    <FaCheck className="check-icon" />
                                )}
                                {loadingLang === lang.code && (
                                    <FaSpinner className="loading-icon spinning" />
                                )}
                                {lang.rtl && (
                                    <span className="rtl-badge" title="Right-to-Left">RTL</span>
                                )}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default LanguageSwitcher;
