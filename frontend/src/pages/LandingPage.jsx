import React from 'react';
import { Link } from 'react-router-dom';
import { FaHeartbeat, FaUserMd, FaCalendarCheck, FaBrain, FaShieldAlt, FaClock } from 'react-icons/fa';
import './LandingPage.css';

const LandingPage = () => {
    return (
        <div className="landing-page">
            {/* Navigation */}
            <nav className="landing-nav">
                <div className="container">
                    <div className="nav-content">
                        <div className="logo">
                            <FaHeartbeat className="logo-icon" />
                            <span>SmartHealth</span>
                        </div>
                        <div className="nav-links">
                            <Link to="/login" className="btn btn-secondary">Login</Link>
                            <Link to="/register" className="btn btn-primary">Get Started</Link>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="hero">
                <div className="container">
                    <div className="hero-content">
                        <div className="hero-badge">
                            <FaBrain /> AI-Powered Healthcare
                        </div>
                        <h1>Smart Patient Healthcare System</h1>
                        <p className="hero-subtitle">
                            Experience the future of healthcare with our AI-powered symptom analysis.
                            Get instant disease predictions and connect with the right specialists.
                        </p>
                        <div className="hero-buttons">
                            <Link to="/register" className="btn btn-primary btn-lg">
                                Start Free Consultation
                            </Link>
                            <Link to="/login" className="btn btn-secondary btn-lg">
                                I have an account
                            </Link>
                        </div>
                        <div className="hero-stats">
                            <div className="stat">
                                <span className="stat-value">95%</span>
                                <span className="stat-label">Prediction Accuracy</span>
                            </div>
                            <div className="stat">
                                <span className="stat-value">40+</span>
                                <span className="stat-label">Diseases Covered</span>
                            </div>
                            <div className="stat">
                                <span className="stat-value">24/7</span>
                                <span className="stat-label">AI Available</span>
                            </div>
                        </div>
                    </div>
                    <div className="hero-visual">
                        <div className="hero-card">
                            <div className="pulse-ring"></div>
                            <FaHeartbeat className="hero-icon" />
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="features">
                <div className="container">
                    <div className="section-header">
                        <h2>Why Choose SmartHealth?</h2>
                        <p>Advanced AI technology meets compassionate healthcare</p>
                    </div>
                    <div className="features-grid">
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaBrain />
                            </div>
                            <h3>AI Symptom Analysis</h3>
                            <p>Our Naive Bayes ML model analyzes your symptoms and predicts potential conditions with high accuracy.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaUserMd />
                            </div>
                            <h3>Specialist Matching</h3>
                            <p>Get automatically matched with the right medical specialist based on your predicted condition.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaCalendarCheck />
                            </div>
                            <h3>Easy Appointments</h3>
                            <p>Book appointments with doctors seamlessly and manage your healthcare schedule online.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaShieldAlt />
                            </div>
                            <h3>Secure & Private</h3>
                            <p>Your health data is protected with enterprise-grade security and encryption.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaClock />
                            </div>
                            <h3>Instant Results</h3>
                            <p>Get disease predictions in seconds, not hours. Quick analysis for timely care.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaHeartbeat />
                            </div>
                            <h3>Health History</h3>
                            <p>Track your symptoms, predictions, and appointments all in one place.</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section className="how-it-works">
                <div className="container">
                    <div className="section-header">
                        <h2>How It Works</h2>
                        <p>Get healthcare guidance in 3 simple steps</p>
                    </div>
                    <div className="steps">
                        <div className="step">
                            <div className="step-number">1</div>
                            <h3>Enter Symptoms</h3>
                            <p>Describe your symptoms using our intuitive interface</p>
                        </div>
                        <div className="step-connector"></div>
                        <div className="step">
                            <div className="step-number">2</div>
                            <h3>AI Analysis</h3>
                            <p>Our ML model predicts potential diseases and specializations</p>
                        </div>
                        <div className="step-connector"></div>
                        <div className="step">
                            <div className="step-number">3</div>
                            <h3>Book Doctor</h3>
                            <p>Schedule an appointment with a recommended specialist</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="cta">
                <div className="container">
                    <div className="cta-content">
                        <h2>Ready to Experience Smart Healthcare?</h2>
                        <p>Join thousands of patients who trust our AI-powered diagnosis system</p>
                        <Link to="/register" className="btn btn-primary btn-lg">
                            Create Free Account
                        </Link>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="landing-footer">
                <div className="container">
                    <div className="footer-content">
                        <div className="footer-brand">
                            <FaHeartbeat className="logo-icon" />
                            <span>SmartHealth</span>
                        </div>
                        <p>© 2024 Smart Patient Healthcare System. Final Year Project.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
