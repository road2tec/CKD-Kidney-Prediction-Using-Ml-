import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { FaHeartbeat, FaEnvelope, FaLock, FaUser, FaPhone, FaSpinner } from 'react-icons/fa';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useAuth, API_URL } from '../App';
import LanguageSwitcher from '../components/LanguageSwitcher';
import './AuthPages.css';

const RegisterPage = () => {
    const { t } = useTranslation();
    const [formData, setFormData] = useState({
        name: '', email: '', password: '', confirmPassword: '',
        phone: '', age: '', gender: '', blood_group: ''
    });
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { login } = useAuth();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!formData.name || !formData.email || !formData.password) {
            toast.error(t('auth.allFields'));
            return;
        }
        if (formData.password !== formData.confirmPassword) {
            toast.error(t('auth.passwordMismatch'));
            return;
        }
        if (formData.password.length < 6) {
            toast.error(t('register.passwordLength'));
            return;
        }

        setLoading(true);
        try {
            const response = await axios.post(`${API_URL}/register`, formData);
            if (response.data.success) {
                login(response.data.user, response.data.token);
                toast.success(t('register.success'));
                navigate('/patient');
            }
        } catch (error) {
            toast.error(error.response?.data?.message || t('auth.registrationFailed'));
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
                            <span>🏥</span>
                            <span>{t('register.healthcare')}</span>
                        </div>
                        <div className="floating-card card-2">
                            <span>🔬</span>
                            <span>{t('register.aiAnalysis')}</span>
                        </div>
                        <div className="floating-card card-3">
                            <span>💊</span>
                            <span>{t('register.treatment')}</span>
                        </div>
                    </div>
                    <h2>{t('register.patientRegistration')}</h2>
                    <p>{t('register.createPatientAccount')}</p>
                </div>

                <div className="auth-right">
                    <div className="auth-form-container">
                        <h1>{t('register.patientRegistration')}</h1>
                        <p className="auth-subtitle">{t('register.registerSubtitle')}</p>

                        <div className="role-info-box">
                            <span className="role-badge">👤 {t('register.patientAccount')}</span>
                            <p className="text-sm text-gray-500">{t('register.doctorNote')}</p>
                        </div>

                        <form onSubmit={handleSubmit} className="auth-form">
                            <div className="form-row">
                                <div className="form-group">
                                    <label className="form-label">{t('register.fullName')} *</label>
                                    <div className="input-with-icon">
                                        <FaUser className="input-icon" />
                                        <input type="text" name="name" className="form-input"
                                            placeholder={t('register.namePlaceholder')} value={formData.name} onChange={handleChange} />
                                    </div>
                                </div>
                                <div className="form-group">
                                    <label className="form-label">{t('auth.phone')}</label>
                                    <div className="input-with-icon">
                                        <FaPhone className="input-icon" />
                                        <input type="tel" name="phone" className="form-input"
                                            placeholder="9876543210" value={formData.phone} onChange={handleChange} />
                                    </div>
                                </div>
                            </div>

                            <div className="form-group">
                                <label className="form-label">{t('auth.email')} *</label>
                                <div className="input-with-icon">
                                    <FaEnvelope className="input-icon" />
                                    <input type="email" name="email" className="form-input"
                                        placeholder={t('auth.enterEmail')} value={formData.email} onChange={handleChange} />
                                </div>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label className="form-label">{t('auth.password')} *</label>
                                    <div className="input-with-icon">
                                        <FaLock className="input-icon" />
                                        <input type="password" name="password" className="form-input"
                                            placeholder="••••••••" value={formData.password} onChange={handleChange} />
                                    </div>
                                </div>
                                <div className="form-group">
                                    <label className="form-label">{t('auth.confirmPassword')} *</label>
                                    <div className="input-with-icon">
                                        <FaLock className="input-icon" />
                                        <input type="password" name="confirmPassword" className="form-input"
                                            placeholder="••••••••" value={formData.confirmPassword} onChange={handleChange} />
                                    </div>
                                </div>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label className="form-label">{t('register.age')}</label>
                                    <input type="number" name="age" className="form-input"
                                        placeholder="25" value={formData.age} onChange={handleChange} />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">{t('register.gender')}</label>
                                    <select name="gender" className="form-select" value={formData.gender} onChange={handleChange}>
                                        <option value="">{t('register.select')}</option>
                                        <option value="male">{t('register.male')}</option>
                                        <option value="female">{t('register.female')}</option>
                                        <option value="other">{t('register.other')}</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label className="form-label">{t('register.bloodGroup')}</label>
                                    <select name="blood_group" className="form-select" value={formData.blood_group} onChange={handleChange}>
                                        <option value="">{t('register.select')}</option>
                                        <option value="A+">A+</option>
                                        <option value="A-">A-</option>
                                        <option value="B+">B+</option>
                                        <option value="B-">B-</option>
                                        <option value="O+">O+</option>
                                        <option value="O-">O-</option>
                                        <option value="AB+">AB+</option>
                                        <option value="AB-">AB-</option>
                                    </select>
                                </div>
                            </div>

                            <button type="submit" className="btn btn-primary btn-lg w-full" disabled={loading}>
                                {loading ? <><FaSpinner className="spin" /> {t('auth.creatingAccount')}</> : t('auth.createAccount')}
                            </button>
                        </form>

                        <div className="auth-footer">
                            <p>{t('auth.haveAccount')} <Link to="/login">{t('auth.signIn')}</Link></p>
                            <p className="text-sm text-gray-500 mt-2">{t('register.areYouDoctor')} <Link to="/login">{t('register.loginHere')}</Link> {t('register.credentialsFromAdmin')}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RegisterPage;
