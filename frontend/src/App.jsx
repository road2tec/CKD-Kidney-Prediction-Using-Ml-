import React, { createContext, useContext, useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import { useTranslation } from 'react-i18next';
import 'react-toastify/dist/ReactToastify.css';
import './i18n'; // Initialize i18n

// Translation Provider
import { TranslationProvider } from './context/TranslationContext';

// Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import PatientDashboard from './pages/PatientDashboard';
import DoctorDashboard from './pages/DoctorDashboard';
import AdminDashboard from './pages/AdminDashboard';

// Auth Context
const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

// API base URL
export const API_URL = 'http://localhost:5000/api';

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles }) => {
    const { user, loading } = useAuth();
    const { t } = useTranslation();

    if (loading) {
        return (
            <div className="loading-overlay">
                <div className="spinner"></div>
                <p>{t('common.loading', 'Loading...')}</p>
            </div>
        );
    }

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    if (allowedRoles && !allowedRoles.includes(user.role)) {
        return <Navigate to="/" replace />;
    }

    return children;
};

// Language-aware Toast Component
const TranslatedToast = () => {
    const { i18n } = useTranslation();

    // Update toast position for RTL languages
    useEffect(() => {
        const isRTL = i18n.language === 'ur';
        // Re-configure toasts when language changes
        document.documentElement.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
    }, [i18n.language]);

    return (
        <ToastContainer
            position={i18n.language === 'ur' ? 'top-left' : 'top-right'}
            autoClose={3000}
            hideProgressBar={false}
            newestOnTop
            closeOnClick
            pauseOnHover
            theme="light"
            rtl={i18n.language === 'ur'}
        />
    );
};

function App() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const { t, i18n } = useTranslation();

    useEffect(() => {
        // Check for saved auth on mount
        const savedUser = localStorage.getItem('user');
        const savedToken = localStorage.getItem('token');

        if (savedUser && savedToken) {
            setUser(JSON.parse(savedUser));
        }
        setLoading(false);
    }, []);

    // Sync document direction with language
    useEffect(() => {
        const isRTL = i18n.language === 'ur';
        document.documentElement.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
        document.documentElement.setAttribute('lang', i18n.language);
    }, [i18n.language]);

    const login = (userData, token) => {
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('token', token);
        setUser(userData);
        toast.success(t('auth.welcomeBack', 'Welcome back') + `, ${userData.name}!`);
    };

    const logout = () => {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        setUser(null);
        toast.info(t('common.logout', 'Logged out successfully'));
    };

    const getToken = () => localStorage.getItem('token');

    return (
        <AuthContext.Provider value={{ user, login, logout, loading, getToken }}>
            <TranslationProvider>
                <BrowserRouter>
                    <Routes>
                        <Route path="/" element={<LandingPage />} />
                        <Route path="/login" element={<LoginPage />} />
                        <Route path="/register" element={<RegisterPage />} />
                        <Route path="/signup" element={<RegisterPage />} />

                        <Route path="/patient/*" element={
                            <ProtectedRoute allowedRoles={['patient']}>
                                <PatientDashboard />
                            </ProtectedRoute>
                        } />

                        <Route path="/doctor/*" element={
                            <ProtectedRoute allowedRoles={['doctor']}>
                                <DoctorDashboard />
                            </ProtectedRoute>
                        } />

                        <Route path="/admin/*" element={
                            <ProtectedRoute allowedRoles={['admin']}>
                                <AdminDashboard />
                            </ProtectedRoute>
                        } />

                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </BrowserRouter>

                <TranslatedToast />
            </TranslationProvider>
        </AuthContext.Provider>
    );
}

export default App;
