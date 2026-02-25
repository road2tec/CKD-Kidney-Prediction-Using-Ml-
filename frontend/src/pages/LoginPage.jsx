import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { FaHeartbeat, FaEnvelope, FaLock, FaSpinner } from 'react-icons/fa';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useAuth, API_URL } from '../App';
import LanguageSwitcher from '../components/LanguageSwitcher';
import './AuthPages.css';

const LoginPage = () => {
    const { t } = useTranslation();
    const [formData, setFormData] = useState({ email: '', password: '' });
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { login } = useAuth();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!formData.email || !formData.password) {
            toast.error(t('auth.allFields'));
            return;
        }

        setLoading(true);
        try {
            const response = await axios.post(`${API_URL}/login`, formData);
            if (response.data.success) {
                login(response.data.user, response.data.token);
                // Redirect based on role
                const role = response.data.user.role;
                if (role === 'patient') navigate('/patient');
                else if (role === 'doctor') navigate('/doctor');
                else if (role === 'admin') navigate('/admin');
            }
        } catch (error) {
            toast.error(error.response?.data?.message || t('auth.loginFailed'));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <LanguageSwitcher />
            <div className="auth-container">
                <div className="auth-left">
                    <div className="auth-brand">
                        <Link to="/" className="logo">
                            <FaHeartbeat className="logo-icon" />
                            <span>{t('landing.brand')}</span>
                        </Link>
                    </div>
                    <div className="auth-illustration">
                        <div className="floating-card card-1">
                            <FaHeartbeat />
                            <span>{t('auth.aiDiagnosis')}</span>
                        </div>
                        <div className="floating-card card-2">
                            <span>🩺</span>
                            <span>{t('auth.expertDoctors')}</span>
                        </div>
                        <div className="floating-card card-3">
                            <span>📅</span>
                            <span>{t('auth.easyBooking')}</span>
                        </div>
                    </div>
                    <h2>{t('auth.welcomeBack')}</h2>
                    <p>{t('auth.accessDashboard')}</p>
                </div>

                <div className="auth-right">
                    <div className="auth-form-container">
                        <h1>{t('auth.signIn')}</h1>
                        <p className="auth-subtitle">{t('auth.enterCredentials')}</p>

                        <form onSubmit={handleSubmit} className="auth-form">
                            <div className="form-group">
                                <label className="form-label">{t('auth.email')}</label>
                                <div className="input-with-icon">
                                    <FaEnvelope className="input-icon" />
                                    <input
                                        type="email"
                                        name="email"
                                        className="form-input"
                                        placeholder={t('auth.enterEmail')}
                                        value={formData.email}
                                        onChange={handleChange}
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label className="form-label">{t('auth.password')}</label>
                                <div className="input-with-icon">
                                    <FaLock className="input-icon" />
                                    <input
                                        type="password"
                                        name="password"
                                        className="form-input"
                                        placeholder={t('auth.enterPassword')}
                                        value={formData.password}
                                        onChange={handleChange}
                                    />
                                </div>
                            </div>

                            <button type="submit" className="btn btn-primary btn-lg w-full" disabled={loading}>
                                {loading ? <><FaSpinner className="spin" /> {t('auth.signingIn')}</> : t('auth.signIn')}
                            </button>
                        </form>

                        <div className="auth-footer">
                            <p>{t('auth.noAccount')} <Link to="/register">{t('auth.createAccount')}</Link></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
