import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { FaHeartbeat, FaCalendarAlt, FaUsers, FaCheck, FaTimes, FaSignOutAlt, FaUser, FaClock, FaChartBar } from 'react-icons/fa';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useAuth, API_URL } from '../App';
import './Dashboard.css';

// Appointments Component
const DoctorAppointments = () => {
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
                <h1><FaCalendarAlt /> Appointments</h1>
                <p>Manage your patient appointments</p>
            </div>

            <div className="filter-tabs mb-4">
                {['all', 'pending', 'confirmed', 'completed'].map(f => (
                    <button key={f} className={`filter-tab ${filter === f ? 'active' : ''}`} onClick={() => setFilter(f)}>
                        {f.charAt(0).toUpperCase() + f.slice(1)}
                    </button>
                ))}
            </div>

            {appointments.length === 0 ? (
                <div className="empty-state card">
                    <FaCalendarAlt className="empty-icon" />
                    <h3>No Appointments</h3>
                    <p>No {filter !== 'all' ? filter : ''} appointments found</p>
                </div>
            ) : (
                <div className="table-container card">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Patient</th>
                                <th>Date & Time</th>
                                <th>Symptoms</th>
                                <th>Status</th>
                                <th>Actions</th>
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
                                            <div className="action-buttons">
                                                <button className="btn btn-sm btn-success" onClick={() => updateStatus(apt._id, 'confirmed')}><FaCheck /></button>
                                                <button className="btn btn-sm btn-danger" onClick={() => updateStatus(apt._id, 'cancelled')}><FaTimes /></button>
                                            </div>
                                        )}
                                        {apt.status === 'confirmed' && (
                                            <button className="btn btn-sm btn-success" onClick={() => updateStatus(apt._id, 'completed')}>Complete</button>
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
                <h1><FaChartBar /> Dashboard</h1>
                <p>Overview of your practice</p>
            </div>

            <div className="stats-grid">
                <div className="card stat-card">
                    <div className="stat-icon blue"><FaCalendarAlt /></div>
                    <div className="stat-info">
                        <h3>{stats.total}</h3>
                        <p>Total Appointments</p>
                    </div>
                </div>
                <div className="card stat-card">
                    <div className="stat-icon orange"><FaClock /></div>
                    <div className="stat-info">
                        <h3>{stats.today}</h3>
                        <p>Today's Appointments</p>
                    </div>
                </div>
                <div className="card stat-card">
                    <div className="stat-icon purple"><FaUsers /></div>
                    <div className="stat-info">
                        <h3>{stats.pending}</h3>
                        <p>Pending</p>
                    </div>
                </div>
                <div className="card stat-card">
                    <div className="stat-icon green"><FaCheck /></div>
                    <div className="stat-info">
                        <h3>{stats.completed}</h3>
                        <p>Completed</p>
                    </div>
                </div>
            </div>

            <div className="card mt-6">
                <h3 className="mb-4">Quick Actions</h3>
                <div className="flex gap-4">
                    <Link to="/doctor/appointments" className="btn btn-primary">View All Appointments</Link>
                    <Link to="/doctor/appointments?status=pending" className="btn btn-secondary">Pending Approvals</Link>
                </div>
            </div>
        </div>
    );
};

// Main Doctor Dashboard
const DoctorDashboard = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => { logout(); navigate('/'); };

    return (
        <div className="dashboard">
            <aside className="sidebar">
                <div className="sidebar-header">
                    <FaHeartbeat className="sidebar-logo" />
                    <span>SmartHealth</span>
                </div>
                <nav className="sidebar-nav">
                    <Link to="/doctor" className="nav-item"><FaChartBar /> Dashboard</Link>
                    <Link to="/doctor/appointments" className="nav-item"><FaCalendarAlt /> Appointments</Link>
                </nav>
                <div className="sidebar-footer">
                    <div className="user-info">
                        <FaUser className="user-avatar" />
                        <div>
                            <span className="user-name">Dr. {user?.name}</span>
                            <span className="user-role">Doctor</span>
                        </div>
                    </div>
                    <button onClick={handleLogout} className="logout-btn"><FaSignOutAlt /> Logout</button>
                </div>
            </aside>
            <main className="main-content">
                <Routes>
                    <Route path="/" element={<DoctorStats />} />
                    <Route path="/appointments" element={<DoctorAppointments />} />
                </Routes>
            </main>
        </div>
    );
};

export default DoctorDashboard;
