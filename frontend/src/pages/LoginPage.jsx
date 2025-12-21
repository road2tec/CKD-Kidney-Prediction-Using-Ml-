import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaHeartbeat, FaEnvelope, FaLock, FaSpinner } from 'react-icons/fa';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useAuth, API_URL } from '../App';
import './AuthPages.css';

const LoginPage = () => {
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
            toast.error('Please fill in all fields');
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
            toast.error(error.response?.data?.message || 'Login failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-container">
                <div className="auth-left">
                    <div className="auth-brand">
                        <Link to="/" className="logo">
                            <FaHeartbeat className="logo-icon" />
                            <span>CKD Predictor</span>
                        </Link>
                    </div>
                    <div className="auth-illustration">
                        <div className="floating-card card-1">
                            <FaHeartbeat />
                            <span>AI Diagnosis</span>
                        </div>
                        <div className="floating-card card-2">
                            <span>🩺</span>
                            <span>Expert Doctors</span>
                        </div>
                        <div className="floating-card card-3">
                            <span>📅</span>
                            <span>Easy Booking</span>
                        </div>
                    </div>
                    <h2>Welcome Back!</h2>
                    <p>Access your health dashboard and manage appointments</p>
                </div>

                <div className="auth-right">
                    <div className="auth-form-container">
                        <h1>Sign In</h1>
                        <p className="auth-subtitle">Enter your credentials to continue</p>

                        <form onSubmit={handleSubmit} className="auth-form">
                            <div className="form-group">
                                <label className="form-label">Email Address</label>
                                <div className="input-with-icon">
                                    <FaEnvelope className="input-icon" />
                                    <input
                                        type="email"
                                        name="email"
                                        className="form-input"
                                        placeholder="Enter your email"
                                        value={formData.email}
                                        onChange={handleChange}
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Password</label>
                                <div className="input-with-icon">
                                    <FaLock className="input-icon" />
                                    <input
                                        type="password"
                                        name="password"
                                        className="form-input"
                                        placeholder="Enter your password"
                                        value={formData.password}
                                        onChange={handleChange}
                                    />
                                </div>
                            </div>

                            <button type="submit" className="btn btn-primary btn-lg w-full" disabled={loading}>
                                {loading ? <><FaSpinner className="spin" /> Signing in...</> : 'Sign In'}
                            </button>
                        </form>

                        <div className="auth-footer">
                            <p>Don't have an account? <Link to="/register">Create Account</Link></p>
                        </div>

                        {/* <div className="demo-credentials">
                            <p className="text-sm text-gray-500">Demo Credentials:</p>
                            <p className="text-sm"><strong>Admin:</strong> admin@healthcare.com / admin123</p>
                        </div> */}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
