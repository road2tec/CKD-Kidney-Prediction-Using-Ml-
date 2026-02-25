import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { FaHeartbeat, FaCalendarAlt, FaUsers, FaCheck, FaTimes, FaSignOutAlt, FaUser, FaClock, FaChartBar, FaVideo, FaPhoneAlt } from 'react-icons/fa';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useAuth, API_URL } from '../App';
import './Dashboard.css';
import VideoCall from '../components/VideoCall';
import LanguageSwitcher from '../components/LanguageSwitcher';

// Appointments Component
const DoctorAppointments = () => {
    const { t } = useTranslation();
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const { getToken } = useAuth();

    useEffect(() => { fetchAppointments(); }, [filter]);

    const fetchAppointments = async () => {
        try {
            const url = filter === 'all' ? `${API_URL}/doctor/appointments` : `${API_URL}/doctor/appointments?status=${filter}`;
            const response = await axios.get(url, { headers: { Authorization: `Bearer ${getToken()}` } });
            if (response.data.success) setAppointments(response.data.appointments);
        } catch (error) {
            toast.error('Failed to fetch appointments');
        } finally {
            setLoading(false);
        }
    };

    const updateStatus = async (id, status) => {
        try {
            const response = await axios.put(`${API_URL}/doctor/update-status`,
                { appointment_id: id, status },
                { headers: { Authorization: `Bearer ${getToken()}` } }
            );
            if (response.data.success) {
                toast.success(`Appointment ${status}`);
                fetchAppointments();
            }
        } catch (error) {
            toast.error('Failed to update status');
        }
    };

    const getStatusBadge = (status) => {
        const classes = { pending: 'badge-warning', confirmed: 'badge-primary', completed: 'badge-success', cancelled: 'badge-error' };
        return <span className={`badge ${classes[status]}`}>{status}</span>;
    };

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="page-content animate-fadeIn">
            <div className="page-header">
                <h1><FaCalendarAlt /> {t('doctor.appointments')}</h1>
                <p>{t('doctor.manageAppointments')}</p>
            </div>

            <div className="filter-tabs mb-4">
                {['all', 'pending', 'confirmed', 'completed'].map(f => (
                    <button key={f} className={`filter-tab ${filter === f ? 'active' : ''}`} onClick={() => setFilter(f)}>
                        {t(`doctor.${f}`) || f.charAt(0).toUpperCase() + f.slice(1)}
                    </button>
                ))}
            </div>

            {appointments.length === 0 ? (
                <div className="empty-state card">
                    <FaCalendarAlt className="empty-icon" />
                    <h3>{t('doctor.noAppointments')}</h3>
                    <p>{t('doctor.noAppointmentsFound')}</p>
                </div>
            ) : (
                <div className="table-container card">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>{t('doctor.patient')}</th>
                                <th>{t('doctor.dateTime')}</th>
                                <th>{t('doctor.symptoms')}</th>
                                <th>{t('doctor.status')}</th>
                                <th>{t('doctor.actions')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {appointments.map(apt => (
                                <tr key={apt._id}>
                                    <td>
                                        <div className="patient-cell">
                                            <strong>{apt.patient?.name || 'Unknown'}</strong>
                                            <span className="text-sm text-gray-500">{apt.patient?.email}</span>
                                        </div>
                                    </td>
                                    <td>
                                        <div className="date-cell">
                                            <strong>{apt.appointment_date}</strong>
                                            <span>{apt.appointment_time}</span>
                                        </div>
                                    </td>
                                    <td>
                                        <span className="symptoms-preview">{apt.predicted_disease || apt.symptoms?.join(', ') || 'N/A'}</span>
                                    </td>
                                    <td>{getStatusBadge(apt.status)}</td>
                                    <td>
                                        {apt.status === 'pending' && (
                                            <>
                                                <button className="btn btn-sm btn-success mr-2" onClick={() => updateStatus(apt._id, 'confirmed')}>{t('doctor.accept')}</button>
                                                <button className="btn btn-sm btn-outline-danger" onClick={() => updateStatus(apt._id, 'cancelled')}>{t('doctor.cancel')}</button>
                                            </>
                                        )}
                                        {apt.status === 'confirmed' && (
                                            <button className="btn btn-sm btn-success" onClick={() => updateStatus(apt._id, 'completed')}>{t('doctor.complete')}</button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

// Stats Component
const DoctorStats = () => {
    const { t } = useTranslation();
    const [stats, setStats] = useState(null);
    const { getToken } = useAuth();

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await axios.get(`${API_URL}/doctor/stats`, { headers: { Authorization: `Bearer ${getToken()}` } });
                if (response.data.success) setStats(response.data.stats);
            } catch (error) {
                console.error('Failed to fetch stats');
            }
        };
        fetchStats();
    }, []);

    if (!stats) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="page-content animate-fadeIn">
            <div className="page-header">
                <h1><FaChartBar /> {t('doctor.dashboard')}</h1>
                <p>{t('doctor.overviewTitle')}</p>
            </div>

            <div className="stats-grid">
                <div className="card stat-card">
                    <div className="stat-icon blue"><FaCalendarAlt /></div>
                    <div className="stat-info">
                        <h3>{stats.total}</h3>
                        <p>{t('doctor.totalAppointments')}</p>
                    </div>
                </div>
                <div className="card stat-card">
                    <div className="stat-icon orange"><FaClock /></div>
                    <div className="stat-info">
                        <h3>{stats.today}</h3>
                        <p>{t('doctor.todaysAppointments')}</p>
                    </div>
                </div>
                <div className="card stat-card">
                    <div className="stat-icon purple"><FaUsers /></div>
                    <div className="stat-info">
                        <h3>{stats.pending}</h3>
                        <p>{t('doctor.pending')}</p>
                    </div>
                </div>
                <div className="card stat-card">
                    <div className="stat-icon green"><FaCheck /></div>
                    <div className="stat-info">
                        <h3>{stats.completed}</h3>
                        <p>{t('doctor.completed')}</p>
                    </div>
                </div>
            </div>

            <div className="card mt-6">
                <h3 className="mb-4">{t('doctor.quickActions')}</h3>
                <div className="flex gap-4">
                    <Link to="/doctor/appointments" className="btn btn-primary">{t('doctor.viewAllAppointments')}</Link>
                    <Link to="/doctor/appointments?status=pending" className="btn btn-secondary">{t('doctor.pendingApprovals')}</Link>
                </div>
            </div>
        </div>
    );
};

// Telemedicine Component for Doctors
const DoctorTelemedicine = () => {
    const { t } = useTranslation();
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeCall, setActiveCall] = useState(null);
    const { getToken, user } = useAuth();

    useEffect(() => {
        fetchSessions();
    }, []);

    const fetchSessions = async () => {
        try {
            const response = await axios.get(`${API_URL}/telemedicine/my-sessions`,
                { headers: { Authorization: `Bearer ${getToken()}` } }
            );
            if (response.data.success) setSessions(response.data.sessions || []);
        } catch (error) {
            console.error('Failed to fetch telemedicine sessions:', error);
        } finally {
            setLoading(false);
        }
    };

    const joinVideoCall = (session) => {
        axios.put(`${API_URL}/telemedicine/session/${session._id}/update-status`,
            { status: 'active' },
            { headers: { Authorization: `Bearer ${getToken()}` } }
        ).catch(console.error);

        setActiveCall({
            sessionId: session._id,
            token: getToken(),
            patientInfo: {
                name: session.patient_name || 'Patient',
                age: session.patient_age,
                blood_group: session.patient_blood_group
            }
        });
    };

    const handleCallEnd = () => {
        if (activeCall) {
            axios.put(`${API_URL}/telemedicine/session/${activeCall.sessionId}/update-status`,
                { status: 'completed' },
                { headers: { Authorization: `Bearer ${getToken()}` } }
            ).catch(console.error);
        }
        setActiveCall(null);
        fetchSessions();
        toast.info('Consultation ended');
    };

    if (activeCall) {
        return (
            <VideoCall
                sessionId={activeCall.sessionId}
                token={activeCall.token}
                userType="doctor"
                patientInfo={activeCall.patientInfo}
                onCallEnd={handleCallEnd}
            />
        );
    }

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="page-content animate-fadeIn">
            <div className="page-header">
                <h1><FaVideo /> {t('doctor.telemedicineSessions')}</h1>
                <p>{t('doctor.telemedicineDesc')}</p>
            </div>

            <div className="card">
                <h3 style={{ marginBottom: '1rem' }}>{t('doctor.scheduledConsultations')}</h3>
                {sessions.length === 0 ? (
                    <p style={{ color: 'var(--gray-500)' }}>{t('doctor.noSessions')}</p>
                ) : (
                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>{t('doctor.patient')}</th>
                                    <th>{t('doctor.type')}</th>
                                    <th>{t('doctor.scheduledTime')}</th>
                                    <th>{t('doctor.status')}</th>
                                    <th>{t('doctor.actions')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {sessions.map(session => (
                                    <tr key={session._id}>
                                        <td><strong>{session.patient_name || 'Unknown Patient'}</strong></td>
                                        <td>{session.session_type === 'video' ? `📹 ${t('doctor.video')}` : `📞 ${t('doctor.audio')}`}</td>
                                        <td>{new Date(session.scheduled_time).toLocaleString()}</td>
                                        <td>
                                            <span className={`badge ${session.status === 'scheduled' ? 'badge-primary' :
                                                session.status === 'active' ? 'badge-warning' :
                                                    session.status === 'completed' ? 'badge-success' : 'badge-error'
                                                }`}>
                                                {session.status}
                                            </span>
                                        </td>
                                        <td>
                                            {(session.status === 'scheduled' || session.status === 'active') && (
                                                <button
                                                    className="btn btn-success btn-sm"
                                                    onClick={() => joinVideoCall(session)}
                                                    style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                                                >
                                                    <FaPhoneAlt /> {t('doctor.joinCall')}
                                                </button>
                                            )}
                                            {session.status === 'completed' && (
                                                <span style={{ color: 'var(--gray-500)', fontSize: '0.875rem' }}>{t('doctor.completed')}</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

// Main Doctor Dashboard

const DoctorDashboard = () => {
    const { t } = useTranslation();
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => { logout(); navigate('/'); };

    return (
        <div className="dashboard">
            <aside className="sidebar">
                <div className="sidebar-header">
                    <FaHeartbeat className="sidebar-logo" />
                    <span>{t('landing.brand')}</span>
                </div>
                <nav className="sidebar-nav">
                    <Link to="/doctor" className="nav-item"><FaChartBar /> {t('doctor.dashboard')}</Link>
                    <Link to="/doctor/appointments" className="nav-item"><FaCalendarAlt /> {t('doctor.appointments')}</Link>
                    <Link to="/doctor/telemedicine" className="nav-item"><FaVideo /> {t('doctor.telemedicine')}</Link>
                </nav>
                <div className="sidebar-footer">
                    <div className="sidebar-language">
                        <LanguageSwitcher />
                    </div>
                    <div className="user-info">
                        <FaUser className="user-avatar" />
                        <div>
                            <span className="user-name">{t('doctor.welcome')} {user?.name}</span>
                            <span className="user-role">{t('auth.doctor')}</span>
                        </div>
                    </div>
                    <button onClick={handleLogout} className="logout-btn"><FaSignOutAlt /> {t('common.logout')}</button>
                </div>
            </aside>
            <main className="main-content">
                <Routes>
                    <Route path="/" element={<DoctorStats />} />
                    <Route path="/appointments" element={<DoctorAppointments />} />
                    <Route path="/telemedicine" element={<DoctorTelemedicine />} />
                </Routes>
            </main>
        </div>
    );
};

export default DoctorDashboard;
