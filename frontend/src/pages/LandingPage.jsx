import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { FaFlask, FaBrain, FaAppleAlt, FaUsers, FaShieldAlt, FaVideo, FaChartLine, FaMicroscope } from 'react-icons/fa';
import LanguageSwitcher from '../components/LanguageSwitcher';
import './LandingPage.css';

const LandingPage = () => {
    const { t } = useTranslation();

    return (
        <div className="landing-page">
            {/* Navigation */}
            <nav className="landing-nav">
                <div className="container">
                    <div className="nav-content">
                        <div className="logo">
                            <FaFlask className="logo-icon" />
                            <span>{t('landing.brand')}</span>
                        </div>
                        <div className="nav-links">
                            <LanguageSwitcher variant="landing" />
                            <Link to="/login" className="btn btn-secondary">{t('common.login')}</Link>
                            <Link to="/register" className="btn btn-primary">{t('common.register')}</Link>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="hero">
                <div className="container">
                    <div className="hero-content">
                        <div className="hero-badge">
                            <FaBrain /> {t('landing.badge')}
                        </div>
                        <h1>{t('landing.heroTitle')}</h1>
                        <p className="hero-subtitle">
                            {t('landing.heroSubtitle')}
                        </p>
                        <div className="hero-buttons">
                            <Link to="/register" className="btn btn-primary btn-lg">
                                {t('landing.startAssessment')}
                            </Link>
                            <Link to="/login" className="btn btn-secondary btn-lg">
                                {t('landing.haveAccount')}
                            </Link>
                        </div>
                        <div className="hero-stats">
                            <div className="stat">
                                <span className="stat-value">96%</span>
                                <span className="stat-label">{t('landing.stats.accuracy')}</span>
                            </div>
                            <div className="stat">
                                <span className="stat-value">24</span>
                                <span className="stat-label">{t('landing.stats.parameters')}</span>
                            </div>
                            <div className="stat">
                                <span className="stat-value">100%</span>
                                <span className="stat-label">{t('landing.stats.explainability')}</span>
                            </div>
                        </div>
                    </div>
                    <div className="hero-visual">
                        <div className="hero-card">
                            <div className="pulse-ring"></div>
                            <FaMicroscope className="hero-icon" />
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="features">
                <div className="container">
                    <div className="section-header">
                        <h2>{t('landing.features.title')}</h2>
                        <p>{t('landing.features.subtitle')}</p>
                    </div>
                    <div className="features-grid">
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaFlask />
                            </div>
                            <h3>{t('landing.features.prediction.title')}</h3>
                            <p>{t('landing.features.prediction.description')}</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaBrain />
                            </div>
                            <h3>{t('landing.features.xai.title')}</h3>
                            <p>{t('landing.features.xai.description')}</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaAppleAlt />
                            </div>
                            <h3>{t('landing.features.diet.title')}</h3>
                            <p>{t('landing.features.diet.description')}</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaUsers />
                            </div>
                            <h3>{t('landing.features.donor.title')}</h3>
                            <p>{t('landing.features.donor.description')}</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaVideo />
                            </div>
                            <h3>{t('landing.features.telemedicine.title')}</h3>
                            <p>{t('landing.features.telemedicine.description')}</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaChartLine />
                            </div>
                            <h3>{t('landing.features.risk.title')}</h3>
                            <p>{t('landing.features.risk.description')}</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section className="how-it-works">
                <div className="container">
                    <div className="section-header">
                        <h2>{t('landing.howItWorks.title')}</h2>
                        <p>{t('landing.howItWorks.subtitle')}</p>
                    </div>
                    <div className="steps">
                        <div className="step">
                            <div className="step-number">1</div>
                            <h3>{t('landing.howItWorks.step1.title')}</h3>
                            <p>{t('landing.howItWorks.step1.description')}</p>
                        </div>
                        <div className="step-connector"></div>
                        <div className="step">
                            <div className="step-number">2</div>
                            <h3>{t('landing.howItWorks.step2.title')}</h3>
                            <p>{t('landing.howItWorks.step2.description')}</p>
                        </div>
                        <div className="step-connector"></div>
                        <div className="step">
                            <div className="step-number">3</div>
                            <h3>{t('landing.howItWorks.step3.title')}</h3>
                            <p>{t('landing.howItWorks.step3.description')}</p>
                        </div>
                        <div className="step-connector"></div>
                        <div className="step">
                            <div className="step-number">4</div>
                            <h3>{t('landing.howItWorks.step4.title')}</h3>
                            <p>{t('landing.howItWorks.step4.description')}</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Why CKD Detection Matters */}
            <section className="why-section">
                <div className="container">
                    <div className="section-header">
                        <h2>{t('landing.why.title')}</h2>
                        <p>{t('landing.why.subtitle')}</p>
                    </div>
                    <div className="why-grid">
                        <div className="why-card">
                            <h3>{t('landing.why.silent.title')}</h3>
                            <p>{t('landing.why.silent.description')}</p>
                        </div>
                        <div className="why-card">
                            <h3>{t('landing.why.preventable.title')}</h3>
                            <p>{t('landing.why.preventable.description')}</p>
                        </div>
                        <div className="why-card">
                            <h3>{t('landing.why.expensive.title')}</h3>
                            <p>{t('landing.why.expensive.description')}</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="cta">
                <div className="container">
                    <div className="cta-content">
                        <h2>{t('landing.cta.title')}</h2>
                        <p>{t('landing.cta.subtitle')}</p>
                        <Link to="/register" className="btn btn-primary btn-lg">
                            {t('landing.cta.button')}
                        </Link>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="landing-footer">
                <div className="container">
                    <div className="footer-content">
                        <div className="footer-brand">
                            <FaFlask className="logo-icon" />
                            <span>{t('landing.brand')}</span>
                        </div>
                        <p>{t('landing.footer.copyright')}</p>
                        <p className="disclaimer">{t('landing.footer.disclaimer')}</p>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
