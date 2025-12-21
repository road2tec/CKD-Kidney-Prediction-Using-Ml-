import React from 'react';
import { Link } from 'react-router-dom';
import { FaFlask, FaBrain, FaAppleAlt, FaUsers, FaShieldAlt, FaVideo, FaChartLine, FaMicroscope } from 'react-icons/fa';
import './LandingPage.css';

const LandingPage = () => {
    return (
        <div className="landing-page">
            {/* Navigation */}
            <nav className="landing-nav">
                <div className="container">
                    <div className="nav-content">
                        <div className="logo">
                            <FaFlask className="logo-icon" />
                            <span>CKD Predictor</span>
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
                            <FaBrain /> Explainable AI-Powered Detection
                        </div>
                        <h1>Chronic Kidney Disease Prediction System</h1>
                        <p className="hero-subtitle">
                            Advanced AI-powered early detection of Chronic Kidney Disease with transparent
                            SHAP-based explanations. Get personalized health recommendations, donor matching,
                            and telemedicine support all in one comprehensive platform.
                        </p>
                        <div className="hero-buttons">
                            <Link to="/register" className="btn btn-primary btn-lg">
                                Start CKD Risk Assessment
                            </Link>
                            <Link to="/login" className="btn btn-secondary btn-lg">
                                I have an account
                            </Link>
                        </div>
                        <div className="hero-stats">
                            <div className="stat">
                                <span className="stat-value">96%</span>
                                <span className="stat-label">CKD Detection Accuracy</span>
                            </div>
                            <div className="stat">
                                <span className="stat-value">24</span>
                                <span className="stat-label">Medical Parameters</span>
                            </div>
                            <div className="stat">
                                <span className="stat-value">100%</span>
                                <span className="stat-label">AI Explainability</span>
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
                        <h2>Complete CKD Care Solution</h2>
                        <p>AI-powered prediction with comprehensive patient support</p>
                    </div>
                    <div className="features-grid">
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaFlask />
                            </div>
                            <h3>CKD Prediction</h3>
                            <p>Advanced Random Forest & Decision Tree models trained on clinical data achieve 96% accuracy in CKD detection.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaBrain />
                            </div>
                            <h3>Explainable AI (XAI)</h3>
                            <p>SHAP-based explanations show exactly why the AI made its prediction. Full transparency for doctors and patients.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaAppleAlt />
                            </div>
                            <h3>Personalized Diet & Lifestyle</h3>
                            <p>Get stage-specific recommendations for diet, exercise, and medication based on your CKD risk level.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaUsers />
                            </div>
                            <h3>Donor-Patient Matching</h3>
                            <p>Blood group compatibility algorithm connects CKD patients with potential kidney donors efficiently.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaVideo />
                            </div>
                            <h3>Telemedicine Support</h3>
                            <p>Virtual consultations with nephrologists, consultation notes, and follow-up scheduling all in one place.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">
                                <FaChartLine />
                            </div>
                            <h3>Risk Level Assessment</h3>
                            <p>Not just prediction - get Low, Medium, or High risk classification based on comprehensive analysis.</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section className="how-it-works">
                <div className="container">
                    <div className="section-header">
                        <h2>How It Works</h2>
                        <p>CKD risk assessment in 4 transparent steps</p>
                    </div>
                    <div className="steps">
                        <div className="step">
                            <div className="step-number">1</div>
                            <h3>Enter Medical Tests</h3>
                            <p>Input 24 medical parameters including creatinine, urea, hemoglobin, and blood pressure</p>
                        </div>
                        <div className="step-connector"></div>
                        <div className="step">
                            <div className="step-number">2</div>
                            <h3>AI Analysis</h3>
                            <p>Random Forest model processes data and predicts CKD risk with 96% accuracy</p>
                        </div>
                        <div className="step-connector"></div>
                        <div className="step">
                            <div className="step-number">3</div>
                            <h3>XAI Explanation</h3>
                            <p>SHAP shows which test results contributed most to the prediction and why</p>
                        </div>
                        <div className="step-connector"></div>
                        <div className="step">
                            <div className="step-number">4</div>
                            <h3>Get Recommendations</h3>
                            <p>Receive personalized diet, lifestyle advice, and access to telemedicine & donor matching</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Why CKD Detection Matters */}
            <section className="why-section">
                <div className="container">
                    <div className="section-header">
                        <h2>Why Early CKD Detection Matters</h2>
                        <p>Chronic Kidney Disease affects 10% of the global population</p>
                    </div>
                    <div className="why-grid">
                        <div className="why-card">
                            <h3>Silent Killer</h3>
                            <p>CKD often shows no symptoms until 75% of kidney function is lost. Early detection saves lives.</p>
                        </div>
                        <div className="why-card">
                            <h3>Preventable Progression</h3>
                            <p>Caught early, CKD progression can be slowed or even reversed with proper care and lifestyle changes.</p>
                        </div>
                        <div className="why-card">
                            <h3>Expensive Late Treatment</h3>
                            <p>Dialysis and transplants cost lakhs. Early detection and prevention is far more affordable.</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="cta">
                <div className="container">
                    <div className="cta-content">
                        <h2>Ready to Check Your Kidney Health?</h2>
                        <p>Join the AI-powered CKD early detection revolution. Free screening available.</p>
                        <Link to="/register" className="btn btn-primary btn-lg">
                            Start Free CKD Risk Assessment
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
                            <span>CKD Predictor</span>
                        </div>
                        <p>© 2024 Chronic Kidney Disease Prediction System with Explainable AI. Final Year Project.</p>
                        <p className="disclaimer">This is a screening tool, not a replacement for professional medical diagnosis.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
