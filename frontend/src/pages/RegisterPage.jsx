import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaHeartbeat, FaEnvelope, FaLock, FaUser, FaPhone, FaSpinner } from 'react-icons/fa';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useAuth, API_URL } from '../App';
import './AuthPages.css';

const RegisterPage = () => {
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
            toast.error('Please fill in required fields');
            return;
        }
        if (formData.password !== formData.confirmPassword) {
            toast.error('Passwords do not match');
            return;
        }
        if (formData.password.length < 6) {
            toast.error('Password must be at least 6 characters');
            return;
        }

        setLoading(true);
        try {
            const response = await axios.post(`${API_URL}/register`, formData);
            if (response.data.success) {
                login(response.data.user, response.data.token);
                toast.success('Account created successfully!');
                navigate('/patient');
            }
        } catch (error) {
            toast.error(error.response?.data?.message || 'Registration failed');
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
                            <span>SmartHealth</span>
                        </Link>
                    </div>
                    <div className="auth-illustration">
                        <div className="floating-card card-1">
                            <span>🏥</span>
                            <span>Healthcare</span>
                        </div>
                        <div className="floating-card card-2">
                            <span>🔬</span>
                            <span>AI Analysis</span>
                        </div>
                        <div className="floating-card card-3">
                            <span>💊</span>
                            <span>Treatment</span>
                        </div>
                    </div>
                    <h2>Patient Registration</h2>
                    <p>Create a patient account to access AI-powered healthcare services</p>
                </div>

                <div className="auth-right">
                    <div className="auth-form-container">
                        <h1>Patient Registration</h1>
                        <p className="auth-subtitle">Register as a patient to use symptom checker & book appointments</p>

                        <div className="role-info-box">
                            <span className="role-badge">👤 Patient Account</span>
                            <p className="text-sm text-gray-500">Doctors are added by admin. If you're a doctor, please contact the administrator.</p>
                        </div>

                        <form onSubmit={handleSubmit} className="auth-form">
                            <div className="form-row">
                                <div className="form-group">
                                    <label className="form-label">Full Name *</label>
                                    <div className="input-with-icon">
                                        <FaUser className="input-icon" />
                                        <input type="text" name="name" className="form-input"
                                            placeholder="John Doe" value={formData.name} onChange={handleChange} />
                                    </div>
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Phone Number</label>
                                    <div className="input-with-icon">
                                        <FaPhone className="input-icon" />
                                        <input type="tel" name="phone" className="form-input"
                                            placeholder="9876543210" value={formData.phone} onChange={handleChange} />
                                    </div>
                                </div>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Email Address *</label>
                                <div className="input-with-icon">
                                    <FaEnvelope className="input-icon" />
                                    <input type="email" name="email" className="form-input"
                                        placeholder="john@example.com" value={formData.email} onChange={handleChange} />
                                </div>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label className="form-label">Password *</label>
                                    <div className="input-with-icon">
                                        <FaLock className="input-icon" />
                                        <input type="password" name="password" className="form-input"
                                            placeholder="••••••••" value={formData.password} onChange={handleChange} />
                                    </div>
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Confirm Password *</label>
                                    <div className="input-with-icon">
                                        <FaLock className="input-icon" />
                                        <input type="password" name="confirmPassword" className="form-input"
                                            placeholder="••••••••" value={formData.confirmPassword} onChange={handleChange} />
                                    </div>
                                </div>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label className="form-label">Age</label>
                                    <input type="number" name="age" className="form-input"
                                        placeholder="25" value={formData.age} onChange={handleChange} />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Gender</label>
                                    <select name="gender" className="form-select" value={formData.gender} onChange={handleChange}>
                                        <option value="">Select</option>
                                        <option value="male">Male</option>
                                        <option value="female">Female</option>
                                        <option value="other">Other</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Blood Group</label>
                                    <select name="blood_group" className="form-select" value={formData.blood_group} onChange={handleChange}>
                                        <option value="">Select</option>
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
                                {loading ? <><FaSpinner className="spin" /> Creating Account...</> : 'Create Account'}
                            </button>
                        </form>

                        <div className="auth-footer">
                            <p>Already have an account? <Link to="/login">Sign In</Link></p>
                            <p className="text-sm text-gray-500 mt-2">Are you a doctor? <Link to="/login">Login here</Link> (credentials from admin)</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RegisterPage;
