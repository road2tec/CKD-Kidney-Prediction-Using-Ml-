import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { FaHeartbeat, FaCalendarAlt, FaUsers, FaCheck, FaTimes, FaSignOutAlt, FaUser, FaClock, FaChartBar, FaVideo, FaPhoneAlt, FaFileMedical, FaNotesMedical, FaVials, FaFileUpload, FaHistory, FaChevronDown, FaChevronUp, FaPills, FaExclamationTriangle, FaCheckCircle } from 'react-icons/fa';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useAuth, API_URL } from '../App';
import './Dashboard.css';
import VideoCall from '../components/VideoCall';
import LanguageSwitcher from '../components/LanguageSwitcher';


// ── Patient Medical History Modal ─────────────────────────────────────
const PatientMedicalHistoryModal = ({ isOpen, onClose, medicalHistory, patientName, loading }) => {
    const { t } = useTranslation();
    const [activeTab, setActiveTab] = useState('profile');
    const [expandedItems, setExpandedItems] = useState({});

    const toggleExpand = (key) => {
        setExpandedItems(prev => ({ ...prev, [key]: !prev[key] }));
    };

    if (!isOpen) return null;

    const history = medicalHistory || {};
    const profile = history.profile || {};
    const pastAppointments = history.past_appointments || [];
    const ckdPredictions = history.ckd_predictions || [];
    const uploadedReports = history.uploaded_reports || [];
    const hybridPredictions = history.hybrid_predictions || [];

    const tabs = [
        { id: 'profile', label: t('doctor.history.profile', 'Patient Profile'), icon: <FaUser />, count: null },
        { id: 'appointments', label: t('doctor.history.pastAppointments', 'Past Appointments'), icon: <FaCalendarAlt />, count: pastAppointments.length },
        { id: 'reports', label: t('doctor.history.uploadedReports', 'Uploaded Reports'), icon: <FaFileUpload />, count: uploadedReports.length },
        { id: 'hybrid', label: t('doctor.history.hybridAI', 'Hybrid AI Predictions'), icon: <FaFileMedical />, count: hybridPredictions.length },
    ];

    const getRiskBadge = (prediction) => {
        if (!prediction) return null;
        const risk = prediction.risk_level || prediction.prediction;
        const isCKD = risk === 'ckd' || risk === 'High' || risk === 'Medium' || prediction.prediction === 1;
        return (
            <span className={`history-badge ${isCKD ? 'badge-danger' : 'badge-safe'}`}>
                {isCKD ? <FaExclamationTriangle /> : <FaCheckCircle />}
                {isCKD ? t('doctor.history.ckdDetected', 'CKD Detected') : t('doctor.history.noCKD', 'No CKD')}
            </span>
        );
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return 'N/A';
        try {
            return new Date(dateStr).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' });
        } catch {
            return dateStr;
        }
    };

    return (
        <div className="medical-history-overlay" onClick={onClose}>
            <div className="medical-history-modal" onClick={e => e.stopPropagation()}>
                {/* Header */}
                <div className="mh-header">
                    <div className="mh-header-info">
                        <FaFileMedical className="mh-header-icon" />
                        <div>
                            <h2>{t('doctor.history.title', 'Patient Medical History')}</h2>
                            <p className="mh-patient-name">{patientName || 'Patient'}</p>
                        </div>
                    </div>
                    <button className="mh-close-btn" onClick={onClose}>&times;</button>
                </div>

                {loading ? (
                    <div className="mh-loading">
                        <div className="spinner"></div>
                        <p>{t('doctor.history.loading', 'Loading medical history...')}</p>
                    </div>
                ) : (
                    <>
                        {/* Tab Navigation */}
                        <div className="mh-tabs">
                            {tabs.map(tab => (
                                <button
                                    key={tab.id}
                                    className={`mh-tab ${activeTab === tab.id ? 'active' : ''}`}
                                    onClick={() => setActiveTab(tab.id)}
                                >
                                    {tab.icon}
                                    <span className="mh-tab-label">{tab.label}</span>
                                    {tab.count !== null && <span className="mh-tab-count">{tab.count}</span>}
                                </button>
                            ))}
                        </div>

                        {/* Tab Content */}
                        <div className="mh-content">

                            {/* ── Profile Tab ── */}
                            {activeTab === 'profile' && (
                                <div className="mh-section animate-fadeIn">
                                    <div className="mh-profile-grid">
                                        <div className="mh-profile-card">
                                            <div className="mh-profile-avatar">
                                                <FaUser />
                                            </div>
                                            <h3>{profile.name || 'N/A'}</h3>
                                            <p className="mh-profile-email">{profile.email || 'N/A'}</p>
                                        </div>
                                        <div className="mh-profile-details">
                                            <div className="mh-detail-row">
                                                <span className="mh-detail-label">{t('doctor.history.age', 'Age')}</span>
                                                <span className="mh-detail-value">{profile.age || 'N/A'}</span>
                                            </div>
                                            <div className="mh-detail-row">
                                                <span className="mh-detail-label">{t('doctor.history.gender', 'Gender')}</span>
                                                <span className="mh-detail-value">{profile.gender || 'N/A'}</span>
                                            </div>
                                            <div className="mh-detail-row">
                                                <span className="mh-detail-label">{t('doctor.history.bloodGroup', 'Blood Group')}</span>
                                                <span className="mh-detail-value highlight">{profile.blood_group || 'N/A'}</span>
                                            </div>
                                            <div className="mh-detail-row">
                                                <span className="mh-detail-label">{t('doctor.history.phone', 'Phone')}</span>
                                                <span className="mh-detail-value">{profile.phone || 'N/A'}</span>
                                            </div>
                                            <div className="mh-detail-row">
                                                <span className="mh-detail-label">{t('doctor.history.address', 'Address')}</span>
                                                <span className="mh-detail-value">{profile.address || 'N/A'}</span>
                                            </div>
                                            <div className="mh-detail-row">
                                                <span className="mh-detail-label">{t('doctor.history.memberSince', 'Member Since')}</span>
                                                <span className="mh-detail-value">{formatDate(profile.created_at)}</span>
                                            </div>
                                        </div>
                                    </div>
                                    {/* Medical History Array */}
                                    {profile.medical_history && profile.medical_history.length > 0 && (
                                        <div className="mh-subsection">
                                            <h4><FaNotesMedical /> {t('doctor.history.medicalHistoryNotes', 'Medical History Notes')}</h4>
                                            <div className="mh-notes-list">
                                                {profile.medical_history.map((item, idx) => (
                                                    <div key={idx} className="mh-note-item">{typeof item === 'string' ? item : JSON.stringify(item)}</div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* ── Past Appointments Tab ── */}
                            {activeTab === 'appointments' && (
                                <div className="mh-section animate-fadeIn">
                                    {pastAppointments.length === 0 ? (
                                        <div className="mh-empty">
                                            <FaCalendarAlt />
                                            <p>{t('doctor.history.noAppointments', 'No past appointments found')}</p>
                                        </div>
                                    ) : (
                                        <div className="mh-cards-list">
                                            {pastAppointments.map((apt, idx) => (
                                                <div key={apt._id || idx} className="mh-record-card">
                                                    <div className="mh-record-header" onClick={() => toggleExpand(`apt-${idx}`)}>
                                                        <div className="mh-record-title">
                                                            <FaCalendarAlt className="mh-record-icon" />
                                                            <div>
                                                                <strong>{apt.appointment_date} — {apt.appointment_time}</strong>
                                                                <span className={`badge ${apt.status === 'completed' ? 'badge-success' : apt.status === 'confirmed' ? 'badge-primary' : apt.status === 'cancelled' ? 'badge-error' : 'badge-warning'}`}>
                                                                    {apt.status}
                                                                </span>
                                                            </div>
                                                        </div>
                                                        {expandedItems[`apt-${idx}`] ? <FaChevronUp /> : <FaChevronDown />}
                                                    </div>
                                                    {expandedItems[`apt-${idx}`] && (
                                                        <div className="mh-record-body">
                                                            {apt.predicted_disease && (
                                                                <div className="mh-info-row">
                                                                    <span className="mh-info-label">{t('doctor.history.predictedDisease', 'Predicted Disease')}</span>
                                                                    <span className="mh-info-value">{apt.predicted_disease}</span>
                                                                </div>
                                                            )}
                                                            {apt.symptoms && apt.symptoms.length > 0 && (
                                                                <div className="mh-info-row">
                                                                    <span className="mh-info-label">{t('doctor.history.symptoms', 'Symptoms')}</span>
                                                                    <span className="mh-info-value">{apt.symptoms.join(', ')}</span>
                                                                </div>
                                                            )}
                                                            {apt.doctor && (
                                                                <div className="mh-info-row">
                                                                    <span className="mh-info-label">{t('doctor.history.consultedDoctor', 'Consulted Doctor')}</span>
                                                                    <span className="mh-info-value">Dr. {apt.doctor.name} ({apt.doctor.specialization || 'General'})</span>
                                                                </div>
                                                            )}
                                                            {apt.doctor_notes && (
                                                                <div className="mh-info-row full-width">
                                                                    <span className="mh-info-label"><FaNotesMedical /> {t('doctor.history.doctorNotes', 'Doctor Notes')}</span>
                                                                    <div className="mh-notes-block">{apt.doctor_notes}</div>
                                                                </div>
                                                            )}
                                                            {apt.prescription && (
                                                                <div className="mh-info-row full-width">
                                                                    <span className="mh-info-label"><FaPills /> {t('doctor.history.prescription', 'Prescription')}</span>
                                                                    <div className="mh-notes-block prescription">{apt.prescription}</div>
                                                                </div>
                                                            )}
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* ── Uploaded Reports Tab ── */}
                            {activeTab === 'reports' && (
                                <div className="mh-section animate-fadeIn">
                                    {uploadedReports.length === 0 ? (
                                        <div className="mh-empty">
                                            <FaFileUpload />
                                            <p>{t('doctor.history.noReports', 'No uploaded reports found')}</p>
                                        </div>
                                    ) : (
                                        <div className="mh-cards-list">
                                            {uploadedReports.map((rpt, idx) => (
                                                <div key={rpt._id || idx} className="mh-record-card report-card">
                                                    <div className="mh-record-header" onClick={() => toggleExpand(`rpt-${idx}`)}>
                                                        <div className="mh-record-title">
                                                            <FaFileUpload className="mh-record-icon" />
                                                            <div>
                                                                <strong>{rpt.filename || 'Report'}</strong>
                                                                <span className="mh-record-date">{formatDate(rpt.created_at)}</span>
                                                            </div>
                                                        </div>
                                                        {expandedItems[`rpt-${idx}`] ? <FaChevronUp /> : <FaChevronDown />}
                                                    </div>
                                                    {expandedItems[`rpt-${idx}`] && (
                                                        <div className="mh-record-body">
                                                            {rpt.extracted_values && Object.keys(rpt.extracted_values).length > 0 && (
                                                                <div className="mh-params-grid">
                                                                    <h5>{t('doctor.history.extractedValues', 'Extracted Medical Values')}</h5>
                                                                    <div className="mh-params">
                                                                        {Object.entries(rpt.extracted_values).map(([key, val]) => (
                                                                            <div key={key} className="mh-param-item">
                                                                                <span className="mh-param-key">{key.replace(/_/g, ' ')}</span>
                                                                                <span className="mh-param-val">{String(val)}</span>
                                                                            </div>
                                                                        ))}
                                                                    </div>
                                                                </div>
                                                            )}
                                                            {rpt.prediction_data && Object.keys(rpt.prediction_data).length > 0 && (
                                                                <div className="mh-params-grid">
                                                                    <h5>{t('doctor.history.predictionParams', 'Prediction Parameters')}</h5>
                                                                    <div className="mh-params">
                                                                        {Object.entries(rpt.prediction_data).map(([key, val]) => (
                                                                            <div key={key} className="mh-param-item">
                                                                                <span className="mh-param-key">{key}</span>
                                                                                <span className="mh-param-val">{typeof val === 'number' ? val.toFixed(2) : String(val)}</span>
                                                                            </div>
                                                                        ))}
                                                                    </div>
                                                                </div>
                                                            )}
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* ── Hybrid AI Tab ── */}
                            {activeTab === 'hybrid' && (
                                <div className="mh-section animate-fadeIn">
                                    {hybridPredictions.length === 0 ? (
                                        <div className="mh-empty">
                                            <FaFileMedical />
                                            <p>{t('doctor.history.noHybridResults', 'No hybrid AI prediction results found')}</p>
                                        </div>
                                    ) : (
                                        <div className="mh-cards-list">
                                            {hybridPredictions.map((hp, idx) => (
                                                <div key={hp._id || idx} className="mh-record-card hybrid-card">
                                                    <div className="mh-record-header" onClick={() => toggleExpand(`hyb-${idx}`)}>
                                                        <div className="mh-record-title">
                                                            <FaFileMedical className="mh-record-icon" />
                                                            <div>
                                                                <strong>{formatDate(hp.created_at)}</strong>
                                                                {getRiskBadge(hp)}
                                                            </div>
                                                        </div>
                                                        {expandedItems[`hyb-${idx}`] ? <FaChevronUp /> : <FaChevronDown />}
                                                    </div>
                                                    {expandedItems[`hyb-${idx}`] && (
                                                        <div className="mh-record-body">
                                                            {hp.ensemble_result && (
                                                                <div className="mh-info-row">
                                                                    <span className="mh-info-label">{t('doctor.history.ensembleResult', 'Ensemble Result')}</span>
                                                                    <span className="mh-info-value">{hp.ensemble_result}</span>
                                                                </div>
                                                            )}
                                                            {hp.confidence && (
                                                                <div className="mh-info-row">
                                                                    <span className="mh-info-label">{t('doctor.history.confidence', 'Confidence')}</span>
                                                                    <span className="mh-info-value">{typeof hp.confidence === 'number' ? hp.confidence.toFixed(1) : hp.confidence}%</span>
                                                                </div>
                                                            )}
                                                            {hp.models_used && (
                                                                <div className="mh-info-row">
                                                                    <span className="mh-info-label">{t('doctor.history.modelsUsed', 'Models Used')}</span>
                                                                    <span className="mh-info-value">{Array.isArray(hp.models_used) ? hp.models_used.join(', ') : hp.models_used}</span>
                                                                </div>
                                                            )}
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};


// ── Appointments Component ────────────────────────────────────────────
const DoctorAppointments = () => {
    const { t } = useTranslation();
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const { getToken } = useAuth();

    // Medical history modal state
    const [historyModalOpen, setHistoryModalOpen] = useState(false);
    const [historyData, setHistoryData] = useState(null);
    const [historyLoading, setHistoryLoading] = useState(false);
    const [historyPatientName, setHistoryPatientName] = useState('');

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

    const updateStatus = async (id, status, patientId, patientName) => {
        try {
            const response = await axios.put(`${API_URL}/doctor/update-status`,
                { appointment_id: id, status },
                { headers: { Authorization: `Bearer ${getToken()}` } }
            );
            if (response.data.success) {
                toast.success(`Appointment ${status}`);
                fetchAppointments();

                // If doctor accepted (confirmed) the appointment, show medical history
                if (status === 'confirmed' && response.data.medical_history) {
                    setHistoryData(response.data.medical_history);
                    setHistoryPatientName(patientName || 'Patient');
                    setHistoryModalOpen(true);
                }
            }
        } catch (error) {
            toast.error('Failed to update status');
        }
    };

    const viewPatientHistory = async (patientId, patientName) => {
        setHistoryLoading(true);
        setHistoryPatientName(patientName || 'Patient');
        setHistoryModalOpen(true);
        try {
            const response = await axios.get(`${API_URL}/doctor/patient-history/${patientId}`,
                { headers: { Authorization: `Bearer ${getToken()}` } }
            );
            if (response.data.success) {
                setHistoryData(response.data.medical_history);
            } else {
                toast.error('Failed to load patient history');
            }
        } catch (error) {
            toast.error('Failed to load patient history');
        } finally {
            setHistoryLoading(false);
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
                                        <div className="action-buttons">
                                            {apt.status === 'pending' && (
                                                <>
                                                    <button className="btn btn-sm btn-success mr-2" onClick={() => updateStatus(apt._id, 'confirmed', apt.patient_id, apt.patient?.name)}>
                                                        <FaCheck /> {t('doctor.accept')}
                                                    </button>
                                                    <button className="btn btn-sm btn-outline-danger" onClick={() => updateStatus(apt._id, 'cancelled')}>
                                                        <FaTimes /> {t('doctor.cancel')}
                                                    </button>
                                                </>
                                            )}
                                            {apt.status === 'confirmed' && (
                                                <button className="btn btn-sm btn-success" onClick={() => updateStatus(apt._id, 'completed')}>
                                                    <FaCheck /> {t('doctor.complete')}
                                                </button>
                                            )}
                                            {/* View History Button — always visible for confirmed/completed */}
                                            {(apt.status === 'confirmed' || apt.status === 'completed' || apt.status === 'pending') && apt.patient_id && (
                                                <button
                                                    className="btn btn-sm btn-history"
                                                    onClick={() => viewPatientHistory(apt.patient_id, apt.patient?.name)}
                                                    title={t('doctor.history.viewHistory', 'View Medical History')}
                                                >
                                                    <FaFileMedical /> {t('doctor.history.viewHistory', 'View History')}
                                                </button>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Medical History Modal */}
            <PatientMedicalHistoryModal
                isOpen={historyModalOpen}
                onClose={() => { setHistoryModalOpen(false); setHistoryData(null); }}
                medicalHistory={historyData}
                patientName={historyPatientName}
                loading={historyLoading}
            />
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
