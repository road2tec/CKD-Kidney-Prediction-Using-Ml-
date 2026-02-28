import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { FaHeartbeat, FaCalendarAlt, FaHistory, FaSignOutAlt, FaUser, FaFlask, FaFileDownload, FaSpinner, FaCheckCircle, FaExclamationTriangle, FaVideo, FaPills, FaHandHoldingHeart, FaUserMd, FaPhone, FaClinicMedical, FaPhoneAlt, FaShareAlt, FaWhatsapp, FaEnvelope, FaTimes, FaCopy, FaTelegram } from 'react-icons/fa';
import { toast } from 'react-toastify';
import axios from 'axios';
import { saveAs } from 'file-saver';
import { useAuth, API_URL } from '../App';
import './Dashboard.css';
import CKDTestForm from './CKDTestForm';
import ReportUpload from './ReportUpload';
import VideoCall from '../components/VideoCall';
import LanguageSwitcher from '../components/LanguageSwitcher';
import { DynamicText } from '../context/TranslationContext';


// CKD Test History Component
const CKDTestHistory = () => {
    const { t } = useTranslation();
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showShareModal, setShowShareModal] = useState(false);
    const [selectedRecord, setSelectedRecord] = useState(null);
    const [shareEmail, setShareEmail] = useState('');
    const [sharing, setSharing] = useState(false);
    const { getToken, user } = useAuth();

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        try {
            const response = await axios.get(`${API_URL}/hybrid/history`,
                { headers: { Authorization: `Bearer ${getToken()}` } }
            );
            if (response.data.success) {
                setHistory(response.data.predictions);
            }
        } catch (error) {
            console.error('Failed to fetch history:', error);
        } finally {
            setLoading(false);
        }
    };

    const downloadPdf = async (predictionId) => {
        try {
            toast.info('Generating PDF report...');
            const response = await axios.get(`${API_URL}/xai/report/pdf/${predictionId}`, {
                headers: { Authorization: `Bearer ${getToken()}` },
                responseType: 'blob'
            });
            const blob = new Blob([response.data], { type: 'application/pdf' });
            saveAs(blob, `CKD_Report_${predictionId.substring(0, 8)}.pdf`);
            toast.success('PDF report downloaded!');
        } catch (error) {
            toast.error('Failed to download PDF');
        }
    };

    const openShareModal = (record) => {
        setSelectedRecord(record);
        setShareEmail('');
        setShowShareModal(true);
    };

    const closeShareModal = () => {
        setShowShareModal(false);
        setSelectedRecord(null);
        setShareEmail('');
    };

    const getReportUrl = (predictionId) => {
        // Generate a shareable report URL
        return `${window.location.origin}/report/${predictionId}`;
    };

    const shareViaEmail = async () => {
        if (!shareEmail.trim()) {
            toast.error('Please enter an email address');
            return;
        }

        // Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(shareEmail)) {
            toast.error('Please enter a valid email address');
            return;
        }

        setSharing(true);
        toast.info('Sending email with PDF report...');

        try {
            // Call backend API to send email with PDF attachment
            const response = await axios.post(`${API_URL}/xai/report/share`, {
                prediction_id: selectedRecord._id,
                recipient_email: shareEmail,
                patient_name: user?.name || 'Patient'
            }, {
                headers: { Authorization: `Bearer ${getToken()}` }
            });

            if (response.data.success) {
                toast.success(`✅ Report sent successfully to ${shareEmail}!`);
                closeShareModal();
            } else {
                toast.error(response.data.message || 'Failed to send email');
            }
        } catch (error) {
            console.error('Email share error:', error);
            const errorMessage = error.response?.data?.message || 'Failed to send email. Please try again.';
            toast.error(errorMessage);
        } finally {
            setSharing(false);
        }
    };

    const shareViaWhatsApp = async () => {
        toast.info('Downloading PDF...');

        try {
            // Download the PDF first
            const response = await axios.get(`${API_URL}/xai/report/pdf/${selectedRecord._id}`, {
                headers: { Authorization: `Bearer ${getToken()}` },
                responseType: 'blob'
            });

            const pdfBlob = new Blob([response.data], { type: 'application/pdf' });
            const fileName = `CKD_Report_${selectedRecord._id.substring(0, 8)}.pdf`;

            // Download PDF to user's computer
            saveAs(pdfBlob, fileName);

            // Open WhatsApp with message
            const text = encodeURIComponent(
                `🏥 *CKD Screening Report*\n\n📄 I've downloaded my CKD report PDF to share with you.\n\n👤 *Patient:* ${user?.name || 'Patient'}\n📅 *Date:* ${formatDate(selectedRecord.timestamp)}\n📊 *Result:* ${selectedRecord.prediction?.result === 'ckd' ? '⚠️ CKD Detected' : '✅ No CKD Detected'}\n📈 *Risk Level:* ${selectedRecord.prediction?.risk_level || 'N/A'}\n🎯 *Confidence:* ${selectedRecord.prediction?.confidence?.toFixed(1)}%\n\n📎 *I will attach the PDF file in the next message.*\n\n_Generated by CKD Prediction System_`
            );

            // Open WhatsApp Web
            window.open(`https://web.whatsapp.com/send?text=${text}`, '_blank');

            toast.success('PDF downloaded! WhatsApp opened - attach the PDF file and send.');
            closeShareModal();
        } catch (error) {
            console.error('WhatsApp share error:', error);
            toast.error('Failed to download PDF. Please try again.');
        }
    };

    const shareViaTelegram = async () => {
        toast.info('Downloading PDF...');

        try {
            // Download the PDF first
            const response = await axios.get(`${API_URL}/xai/report/pdf/${selectedRecord._id}`, {
                headers: { Authorization: `Bearer ${getToken()}` },
                responseType: 'blob'
            });

            const pdfBlob = new Blob([response.data], { type: 'application/pdf' });
            const fileName = `CKD_Report_${selectedRecord._id.substring(0, 8)}.pdf`;

            // Download PDF to user's computer
            saveAs(pdfBlob, fileName);

            // Open Telegram with message
            const text = encodeURIComponent(
                `🏥 CKD Screening Report\n\n📄 I've downloaded my CKD report PDF to share with you.\n\n👤 Patient: ${user?.name || 'Patient'}\n📅 Date: ${formatDate(selectedRecord.timestamp)}\n📊 Result: ${selectedRecord.prediction?.result === 'ckd' ? '⚠️ CKD Detected' : '✅ No CKD Detected'}\n📈 Risk Level: ${selectedRecord.prediction?.risk_level || 'N/A'}\n\n📎 I will attach the PDF file next.`
            );

            // Open Telegram Web
            window.open(`https://telegram.me/share/url?url=&text=${text}`, '_blank');

            toast.success('PDF downloaded! Telegram opened - attach the PDF file and send.');
            closeShareModal();
        } catch (error) {
            console.error('Telegram share error:', error);
            toast.error('Failed to download PDF. Please try again.');
        }
    };

    const copyToClipboard = () => {
        const text = `CKD Screening Report\n\nPatient: ${user?.name || 'Patient'}\nDate: ${formatDate(selectedRecord.timestamp)}\nResult: ${selectedRecord.prediction?.result === 'ckd' ? 'CKD Detected' : 'No CKD Detected'}\nRisk Level: ${selectedRecord.prediction?.risk_level || 'N/A'}\nConfidence: ${selectedRecord.prediction?.confidence?.toFixed(1)}%\n\nGenerated by CKD Prediction System`;

        navigator.clipboard.writeText(text).then(() => {
            toast.success('Report details copied to clipboard!');
        }).catch(() => {
            toast.error('Failed to copy');
        });
    };

    const nativeShare = async () => {
        toast.info('Downloading PDF for sharing...');

        try {
            // Download PDF first
            const response = await axios.get(`${API_URL}/xai/report/pdf/${selectedRecord._id}`, {
                headers: { Authorization: `Bearer ${getToken()}` },
                responseType: 'blob'
            });

            const pdfBlob = new Blob([response.data], { type: 'application/pdf' });
            const fileName = `CKD_Report_${selectedRecord._id.substring(0, 8)}.pdf`;
            const pdfFile = new File([pdfBlob], fileName, { type: 'application/pdf' });

            // Use native share if available
            if (navigator.share && navigator.canShare && navigator.canShare({ files: [pdfFile] })) {
                await navigator.share({
                    title: 'CKD Screening Report',
                    text: `CKD Report for ${user?.name || 'Patient'}`,
                    files: [pdfFile]
                });
                toast.success('PDF shared successfully!');
            } else {
                saveAs(pdfBlob, fileName);
                toast.success('PDF downloaded! Use the downloaded file to share.');
            }
            closeShareModal();
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Native share error:', error);
                toast.error('Share failed. Please try Download PDF button.');
            }
        }
    };

    const formatDate = (timestamp) => {
        if (!timestamp) return 'N/A';
        return new Date(timestamp).toLocaleDateString('en-IN', {
            day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
        });
    };

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="page-content animate-fadeIn">
            <div className="page-header">
                <h1><FaHistory /> {t('patient.testHistory')}</h1>
                <p>{t('patient.testHistoryDesc')}</p>
            </div>
            {history.length === 0 ? (
                <div className="empty-state card">
                    <FaFlask className="empty-icon" />
                    <h3>{t('patient.noTests')}</h3>
                    <p>{t('patient.noTestsDesc')}</p>
                    <Link to="/patient" className="btn btn-primary">{t('patient.takeTest')}</Link>
                </div>
            ) : (
                <div className="history-list">
                    {history.map((record) => (
                        <div key={record._id} className="card history-card">
                            <div className="history-header">
                                <div className="history-result">
                                    {record.prediction?.result === 'ckd' ? (
                                        <FaExclamationTriangle className="result-icon warning" />
                                    ) : (
                                        <FaCheckCircle className="result-icon success" />
                                    )}
                                    <div>
                                        <h3>{record.prediction?.result === 'ckd' ? t('patient.ckdDetected') : t('patient.noCkdDetected')}</h3>
                                        <span className="history-date">{formatDate(record.timestamp)}</span>
                                    </div>
                                </div>
                                <span className={`badge ${record.prediction?.risk_level === 'High' ? 'badge-error' : 'badge-success'}`}>
                                    {record.prediction?.risk_level || 'N/A'} {t('patient.riskLevel')}
                                </span>
                            </div>
                            <div className="history-body">
                                <div className="history-metrics">
                                    <div className="metric-item">
                                        <span className="metric-label">{t('patient.confidence')}</span>
                                        <span className="metric-value">{record.prediction?.confidence?.toFixed(1)}%</span>
                                    </div>
                                    <div className="metric-item">
                                        <span className="metric-label">Model</span>
                                        <span className="metric-value">Hybrid AI</span>
                                    </div>
                                </div>
                            </div>
                            <div className="history-footer">
                                <button className="btn btn-outline btn-sm" onClick={() => downloadPdf(record._id)}>
                                    <FaFileDownload /> {t('patient.downloadPdf')}
                                </button>
                                <button className="btn btn-primary btn-sm" onClick={() => openShareModal(record)}>
                                    <FaShareAlt /> {t('patient.shareReport')}
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Share Modal */}
            {showShareModal && selectedRecord && (
                <div className="share-modal-overlay" onClick={closeShareModal}>
                    <div className="share-modal" onClick={(e) => e.stopPropagation()}>
                        <div className="share-modal-header">
                            <h3><FaShareAlt /> {t('patient.shareReport')}</h3>
                            <button className="close-btn" onClick={closeShareModal}><FaTimes /></button>
                        </div>

                        <div className="share-modal-body">
                            <div className="share-report-info">
                                <p><strong>Report Date:</strong> {formatDate(selectedRecord.timestamp)}</p>
                                <p><strong>Result:</strong> {selectedRecord.prediction?.result === 'ckd' ? 'CKD Detected' : 'No CKD Detected'}</p>
                                <p><strong>Risk Level:</strong> {selectedRecord.prediction?.risk_level || 'N/A'}</p>
                            </div>

                            {/* Email Share */}
                            <div className="share-section">
                                <label>Share via Email</label>
                                <div className="share-email-input">
                                    <input
                                        type="email"
                                        className="form-input"
                                        placeholder="Enter recipient email"
                                        value={shareEmail}
                                        onChange={(e) => setShareEmail(e.target.value)}
                                    />
                                    <button
                                        className="btn btn-primary"
                                        onClick={shareViaEmail}
                                        disabled={sharing}
                                    >
                                        {sharing ? <FaSpinner className="spin" /> : <FaEnvelope />}
                                        Send
                                    </button>
                                </div>
                            </div>

                            {/* Quick Share Options */}
                            <div className="share-section">
                                <label>Quick Share</label>
                                <div className="share-buttons">
                                    <button className="share-btn whatsapp" onClick={shareViaWhatsApp}>
                                        <FaWhatsapp /> WhatsApp
                                    </button>
                                    <button className="share-btn telegram" onClick={shareViaTelegram}>
                                        <FaTelegram /> Telegram
                                    </button>
                                    <button className="share-btn copy" onClick={copyToClipboard}>
                                        <FaCopy /> Copy Text
                                    </button>
                                    {navigator.share && (
                                        <button className="share-btn native" onClick={nativeShare}>
                                            <FaShareAlt /> More...
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

// Telemedicine Component
const Telemedicine = () => {
    const { t } = useTranslation();
    const [slots, setSlots] = useState([]);
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeCall, setActiveCall] = useState(null); // { sessionId, token }
    const { getToken, user } = useAuth();

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const sessionsRes = await axios.get(`${API_URL}/telemedicine/my-sessions`,
                { headers: { Authorization: `Bearer ${getToken()}` } }
            );
            if (sessionsRes.data.success) setSessions(sessionsRes.data.sessions || []);

            // Get doctors for slot booking
            const doctorsRes = await axios.get(`${API_URL}/doctors`,
                { headers: { Authorization: `Bearer ${getToken()}` } }
            );
            if (doctorsRes.data.success && doctorsRes.data.doctors?.length > 0) {
                // Generate sample slots for display
                const sampleSlots = [];
                const today = new Date();
                for (let i = 1; i <= 3; i++) {
                    const slotDate = new Date(today);
                    slotDate.setDate(today.getDate() + i);
                    sampleSlots.push({
                        date: slotDate.toLocaleDateString('en-IN', { weekday: 'short', month: 'short', day: 'numeric' }),
                        time: '10:00 AM',
                        datetime: slotDate.toISOString(),
                        doctor_id: doctorsRes.data.doctors[0]._id
                    });
                    sampleSlots.push({
                        date: slotDate.toLocaleDateString('en-IN', { weekday: 'short', month: 'short', day: 'numeric' }),
                        time: '3:00 PM',
                        datetime: slotDate.toISOString(),
                        doctor_id: doctorsRes.data.doctors[0]._id
                    });
                }
                setSlots(sampleSlots);
            }
        } catch (error) {
            console.error('Failed to fetch telemedicine data:', error);
        } finally {
            setLoading(false);
        }
    };

    const createSession = async (doctorId, slotTime) => {
        try {
            await axios.post(`${API_URL}/telemedicine/create-session`,
                { doctor_id: doctorId, session_type: 'video', scheduled_time: slotTime },
                { headers: { Authorization: `Bearer ${getToken()}` } }
            );
            toast.success('Telemedicine session scheduled!');
            fetchData();
        } catch (error) {
            toast.error('Failed to schedule session');
        }
    };

    const startVideoCall = (session) => {
        // Update session status to active
        axios.put(`${API_URL}/telemedicine/session/${session._id}/update-status`,
            { status: 'active' },
            { headers: { Authorization: `Bearer ${getToken()}` } }
        ).catch(console.error);

        setActiveCall({
            sessionId: session._id,
            token: getToken()
        });
    };

    const handleCallEnd = () => {
        if (activeCall) {
            // Update session status to completed
            axios.put(`${API_URL}/telemedicine/session/${activeCall.sessionId}/update-status`,
                { status: 'completed' },
                { headers: { Authorization: `Bearer ${getToken()}` } }
            ).catch(console.error);
        }
        setActiveCall(null);
        fetchData();
        toast.info('Call ended');
    };

    // Show video call if active
    if (activeCall) {
        return (
            <VideoCall
                sessionId={activeCall.sessionId}
                token={activeCall.token}
                userType="patient"
                onCallEnd={handleCallEnd}
            />
        );
    }

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="page-content animate-fadeIn">
            <div className="page-header">
                <h1><FaVideo /> {t('patient.telemedicine')}</h1>
                <p>{t('patient.telemedicineDesc')}</p>
            </div>

            <div className="feature-grid">
                <div className="card feature-card">
                    <div className="feature-icon"><FaVideo /></div>
                    <h3>Video Consultation</h3>
                    <p>Face-to-face video calls with nephrologists for detailed CKD discussions</p>
                </div>
                <div className="card feature-card">
                    <div className="feature-icon"><FaPhone /></div>
                    <h3>Audio Consultation</h3>
                    <p>Quick phone consultations for follow-ups and medication queries</p>
                </div>
                <div className="card feature-card">
                    <div className="feature-icon"><FaUserMd /></div>
                    <h3>Expert Specialists</h3>
                    <p>Connect with verified nephrologists and kidney care specialists</p>
                </div>
            </div>

            <div className="card" style={{ marginTop: '2rem' }}>
                <h3 style={{ marginBottom: '1rem' }}>Available Consultation Slots</h3>
                {slots.length === 0 ? (
                    <p style={{ color: 'var(--gray-500)' }}>No slots available currently. Check back later.</p>
                ) : (
                    <div className="slots-grid">
                        {slots.slice(0, 6).map((slot, idx) => (
                            <div key={idx} className="slot-item">
                                <span>{slot.date} - {slot.time}</span>
                                <button className="btn btn-primary btn-sm" onClick={() => createSession(slot.doctor_id, slot.datetime)}>Book</button>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="card" style={{ marginTop: '2rem' }}>
                <h3 style={{ marginBottom: '1rem' }}>{t('patient.myAppointments')}</h3>
                {sessions.length === 0 ? (
                    <p style={{ color: 'var(--gray-500)' }}>{t('patient.noAppointmentsDesc')}</p>
                ) : (
                    <div className="sessions-list">
                        {sessions.map((session) => (
                            <div key={session._id} className="session-item">
                                <div>
                                    <strong>{session.session_type === 'video' ? '📹 Video' : '📞 Audio'} Consultation</strong>
                                    <p>{new Date(session.scheduled_time).toLocaleString()}</p>
                                    {session.doctor_name && <p style={{ fontSize: '0.875rem', color: 'var(--gray-500)' }}>with Dr. {session.doctor_name}</p>}
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                    <span className={`badge ${session.status === 'scheduled' ? 'badge-primary' : session.status === 'completed' ? 'badge-success' : 'badge-warning'}`}>
                                        {t(`patient.${session.status}`) || session.status}
                                    </span>
                                    {(session.status === 'scheduled' || session.status === 'active') && (
                                        <button
                                            className="btn btn-success btn-sm"
                                            onClick={() => startVideoCall(session)}
                                            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                                        >
                                            <FaPhoneAlt /> Start Call
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

// Donor Matching Component
const DonorMatching = () => {
    const { t } = useTranslation();
    const [donorProfile, setDonorProfile] = useState(null);
    const [matches, setMatches] = useState([]);
    const [stats, setStats] = useState({});
    const [loading, setLoading] = useState(true);
    const [showRegister, setShowRegister] = useState(false);
    const [formData, setFormData] = useState({
        blood_group: '', age: '', weight: '', height: '', is_living_donor: true, contact_phone: ''
    });
    const { getToken, user } = useAuth();

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [profileRes, statsRes] = await Promise.all([
                axios.get(`${API_URL}/donor/my-profile`, { headers: { Authorization: `Bearer ${getToken()}` } }).catch(() => ({ data: { success: false } })),
                axios.get(`${API_URL}/donor/statistics`)
            ]);
            if (profileRes.data.success) setDonorProfile(profileRes.data.donor_profile);
            if (statsRes.data.success) setStats(statsRes.data.statistics || {});
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const registerAsDonor = async () => {
        // Validate required fields
        if (!formData.blood_group) {
            toast.error('Please select a blood group');
            return;
        }
        if (!formData.age || isNaN(parseInt(formData.age))) {
            toast.error('Please enter a valid age');
            return;
        }
        if (!formData.weight || isNaN(parseFloat(formData.weight))) {
            toast.error('Please enter a valid weight');
            return;
        }
        if (!formData.contact_phone) {
            toast.error('Please enter a contact phone number');
            return;
        }

        try {
            const payload = {
                blood_group: formData.blood_group,
                age: parseInt(formData.age),
                weight: parseFloat(formData.weight),
                height: formData.height ? parseFloat(formData.height) : 0,
                contact_phone: formData.contact_phone,
                is_living_donor: formData.is_living_donor
            };
            await axios.post(`${API_URL}/donor/register`, payload, { headers: { Authorization: `Bearer ${getToken()}` } });
            toast.success('Registered as donor successfully!');
            setShowRegister(false);
            setFormData({ blood_group: '', age: '', weight: '', height: '', is_living_donor: true, contact_phone: '' });
            fetchData();
        } catch (error) {
            toast.error(error.response?.data?.message || 'Failed to register as donor');
        }
    };

    const findMatches = async () => {
        try {
            const res = await axios.post(`${API_URL}/donor/match`,
                { blood_group: user?.blood_group || formData.blood_group || 'O+', urgency_level: 'normal' },
                { headers: { Authorization: `Bearer ${getToken()}` } }
            );
            if (res.data.success) setMatches(res.data.compatible_donors || []);
            toast.info(`Found ${res.data.matches_found || 0} compatible donors`);
        } catch (error) {
            toast.error('Failed to find matches');
        }
    };

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="page-content animate-fadeIn">
            <div className="page-header">
                <h1><FaHandHoldingHeart /> {t('patient.donorMatch')}</h1>
                <p>{t('patient.registerAsDonorTitle')}</p>
            </div>

            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-value">{stats.total_registered_donors || 0}</div>
                    <div className="stat-label">{t('patient.registeredDonors')}</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{stats.available_donors || 0}</div>
                    <div className="stat-label">{t('patient.available')}</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{stats.successful_matches || 0}</div>
                    <div className="stat-label">{t('patient.successfulMatches')}</div>
                </div>
            </div>

            <div className="card" style={{ marginTop: '2rem' }}>
                <h3>{t('patient.yourDonorStatus')}</h3>
                {donorProfile ? (
                    <div className="donor-profile">
                        <p><strong>{t('patient.bloodType')}:</strong> {donorProfile.blood_group}</p>
                        <p><strong>{t('patient.status')}:</strong> <span className={`badge ${donorProfile.is_available ? 'badge-success' : 'badge-warning'}`}>
                            {donorProfile.is_available ? t('patient.available') : t('patient.unavailable')}
                        </span></p>
                        <p><strong>{t('patient.registered')}:</strong> {donorProfile.registration_date ? new Date(donorProfile.registration_date).toLocaleDateString() : 'N/A'}</p>
                    </div>
                ) : (
                    <div>
                        <p style={{ marginBottom: '1rem' }}>{t('patient.notRegisteredMsg')}</p>
                        {!showRegister ? (
                            <button className="btn btn-primary" onClick={() => setShowRegister(true)}>
                                <FaHandHoldingHeart /> {t('patient.registerButton')}
                            </button>
                        ) : (
                            <div className="donor-form">
                                <div className="form-row">
                                    <select className="form-select" value={formData.blood_group} onChange={e => setFormData({ ...formData, blood_group: e.target.value })}>
                                        <option value="">{t('patient.bloodType')}</option>
                                        <option value="A+">A+</option><option value="A-">A-</option>
                                        <option value="B+">B+</option><option value="B-">B-</option>
                                        <option value="AB+">AB+</option><option value="AB-">AB-</option>
                                        <option value="O+">O+</option><option value="O-">O-</option>
                                    </select>
                                    <input className="form-input" type="number" placeholder={t('patient.age')} value={formData.age} onChange={e => setFormData({ ...formData, age: e.target.value })} />
                                </div>
                                <div className="form-row">
                                    <input className="form-input" type="number" placeholder={t('patient.weight')} value={formData.weight} onChange={e => setFormData({ ...formData, weight: e.target.value })} />
                                    <input className="form-input" type="tel" placeholder={t('patient.contact')} value={formData.contact_phone} onChange={e => setFormData({ ...formData, contact_phone: e.target.value })} />
                                </div>
                                <button className="btn btn-primary" onClick={registerAsDonor}>{t('patient.submitRegistration')}</button>
                            </div>
                        )}
                    </div>
                )}
            </div>

            <div className="card" style={{ marginTop: '2rem' }}>
                <h3>{t('patient.findCompatibleDonors')}</h3>
                <button className="btn btn-outline" onClick={findMatches} style={{ marginBottom: '1rem' }}>
                    {t('patient.searchMatches')}
                </button>
                {matches.length > 0 && (
                    <div className="matches-list">
                        {matches.map((match, idx) => (
                            <div key={idx} className="match-item" style={{ flexDirection: 'column', alignItems: 'flex-start', padding: '1.5rem', borderBottom: '1px solid #eee' }}>
                                <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                    <div>
                                        <h4 style={{ margin: 0, fontSize: '1.1rem', color: 'var(--primary-700)' }}>
                                            {t('patient.bloodType')}: {match.blood_group}
                                        </h4>
                                        <span style={{ fontSize: '0.85rem', color: 'var(--gray-500)' }}>{t('patient.age')}: {match.age} ({match.age_difference} {t('patient.yearsGap')})</span>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <div className="score-badge" style={{
                                            background: match.compatibility_score >= 80 ? 'var(--success-100)' : 'var(--warning-100)',
                                            color: match.compatibility_score >= 80 ? 'var(--success-700)' : 'var(--warning-700)',
                                            padding: '0.5rem 1rem',
                                            borderRadius: '2rem',
                                            fontWeight: 'bold',
                                            display: 'inline-block'
                                        }}>
                                            {match.compatibility_score}% {t('patient.compatible')}
                                        </div>
                                    </div>
                                </div>

                                <div className="match-reasons" style={{ background: '#f8fafc', padding: '1rem', borderRadius: '0.5rem', width: '100%' }}>
                                    <h5 style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem', color: 'var(--gray-600)' }}>{t('patient.compatibilityBreakdown')}:</h5>
                                    {match.match_reason && match.match_reason.map((reason, rIdx) => (
                                        <div key={rIdx} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem', fontSize: '0.9rem', color: '#475569' }}>
                                            <FaCheckCircle style={{ color: 'var(--success-500)', flexShrink: 0 }} />
                                            <span>{reason}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

// Medicine Search Component - Find medicines and medical stores
const PharmacyMedicine = () => {
    const { t } = useTranslation();
    const [medicals, setMedicals] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState(null);
    const [loading, setLoading] = useState(true);
    const [searching, setSearching] = useState(false);
    const { getToken } = useAuth();

    // Common CKD Medicines list for quick search
    const commonMedicines = [
        'Lisinopril', 'Losartan', 'Amlodipine', 'Metformin', 'Dapagliflozin',
        'Furosemide', 'Erythropoietin', 'Iron Supplements', 'Calcium Acetate',
        'Vitamin D', 'Sodium Bicarbonate', 'Atorvastatin'
    ];

    useEffect(() => {
        fetchMedicals();
    }, []);

    const fetchMedicals = async () => {
        try {
            const res = await axios.get(`${API_URL}/pharmacy/pharmacies`);
            if (res.data.success) setMedicals(res.data.pharmacies || []);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const searchMedicine = (query) => {
        if (!query.trim()) {
            setSearchResults(null);
            return;
        }
        setSearching(true);
        const lowerQuery = query.toLowerCase();

        // Find all medicals that have this medicine
        const results = medicals.filter(medical => {
            if (!medical.available_medicines || medical.available_medicines.length === 0) return false;
            return medical.available_medicines.some(med =>
                med.name?.toLowerCase().includes(lowerQuery) ||
                med.category?.toLowerCase().includes(lowerQuery)
            );
        }).map(medical => ({
            ...medical,
            matchedMedicines: medical.available_medicines.filter(med =>
                med.name?.toLowerCase().includes(lowerQuery) ||
                med.category?.toLowerCase().includes(lowerQuery)
            )
        }));

        setSearchResults(results);
        setSearching(false);
    };

    const handleSearch = () => {
        searchMedicine(searchQuery);
    };

    const clearSearch = () => {
        setSearchQuery('');
        setSearchResults(null);
    };

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="page-content animate-fadeIn">
            <div className="page-header">
                <h1><FaPills /> {t('patient.findMedicines')}</h1>
                <p>{t('patient.findMedicinesDesc')}</p>
            </div>

            {/* Search Section */}
            <div className="card" style={{ marginBottom: '2rem', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                <h3 style={{ marginBottom: '1rem', color: 'white' }}>🔍 {t('patient.searchMedicine')}</h3>
                <div className="flex gap-3" style={{ flexWrap: 'wrap' }}>
                    <input
                        type="text"
                        className="form-input"
                        placeholder={t('patient.enterMedicineName')}
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                        onKeyPress={e => e.key === 'Enter' && handleSearch()}
                        style={{ flex: '1', minWidth: '250px', background: 'rgba(255,255,255,0.95)', color: '#333' }}
                    />
                    <button className="btn" onClick={handleSearch} disabled={searching} style={{ background: 'white', color: '#764ba2', fontWeight: '600' }}>
                        {searching ? <FaSpinner className="spin" /> : t('patient.search')}
                    </button>
                    {searchResults && <button className="btn" onClick={clearSearch} style={{ background: 'rgba(255,255,255,0.3)', color: 'white' }}>{t('patient.clear')}</button>}
                </div>

                {/* Quick Search Pills */}
                <div style={{ marginTop: '1rem' }}>
                    <p style={{ fontSize: '0.85rem', marginBottom: '0.5rem', opacity: 0.9 }}>{t('patient.quickSearch')}:</p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                        {commonMedicines.map((med, idx) => (
                            <button
                                key={idx}
                                onClick={() => { setSearchQuery(med); searchMedicine(med); }}
                                style={{
                                    padding: '0.25rem 0.75rem',
                                    background: 'rgba(255,255,255,0.2)',
                                    border: '1px solid rgba(255,255,255,0.4)',
                                    borderRadius: '20px',
                                    color: 'white',
                                    fontSize: '0.8rem',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                }}
                            >
                                {med}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Search Results */}
            {searchResults && (
                <div className="card" style={{ marginBottom: '2rem' }}>
                    <h3 style={{ marginBottom: '1rem' }}>
                        📍 Medical Stores with "{searchQuery}" ({searchResults.length} found)
                    </h3>
                    {searchResults.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '2rem' }}>
                            <FaPills style={{ fontSize: '3rem', color: 'var(--gray-300)', marginBottom: '1rem' }} />
                            <p style={{ color: 'var(--gray-500)' }}>No medical store found with "{searchQuery}"</p>
                            <p style={{ color: 'var(--gray-400)', fontSize: '0.9rem' }}>Try searching for a different medicine</p>
                        </div>
                    ) : (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1rem' }}>
                            {searchResults.map((medical, idx) => (
                                <div key={idx} style={{
                                    padding: '1.25rem',
                                    background: 'var(--gray-50)',
                                    borderRadius: '12px',
                                    border: '1px solid var(--gray-200)'
                                }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                                        <div>
                                            <h4 style={{ margin: 0, fontSize: '1.1rem' }}>{medical.name}</h4>
                                            <span className="badge badge-primary" style={{ marginTop: '0.25rem' }}>{medical.type}</span>
                                        </div>
                                        {medical.delivers && <span className="badge badge-success">Delivery</span>}
                                    </div>

                                    <div style={{ fontSize: '0.9rem', color: 'var(--gray-600)', marginBottom: '0.75rem' }}>
                                        <p style={{ margin: '0.25rem 0' }}>📍 {medical.address}, {medical.city}{medical.state ? `, ${medical.state}` : ''}</p>
                                        <p style={{ margin: '0.25rem 0' }}>📞 {medical.contact}</p>
                                        <p style={{ margin: '0.25rem 0' }}>⏰ {medical.hours}</p>
                                    </div>

                                    <div style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid var(--gray-200)' }}>
                                        <p style={{ fontWeight: '600', fontSize: '0.85rem', marginBottom: '0.5rem', color: 'var(--primary-600)' }}>
                                            💊 Matched Medicines ({medical.matchedMedicines?.length}):
                                        </p>
                                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                                            {medical.matchedMedicines?.map((med, i) => (
                                                <span key={i} className="badge badge-warning" style={{ fontSize: '0.75rem' }}>
                                                    {med.name}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* All Medical Stores - Show when not searching */}
            {!searchResults && (
                <div className="card">
                    <h3 style={{ marginBottom: '1rem' }}><FaClinicMedical /> All Medical Stores</h3>
                    {medicals.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '2rem' }}>
                            <FaClinicMedical style={{ fontSize: '3rem', color: 'var(--gray-300)', marginBottom: '1rem' }} />
                            <p style={{ color: 'var(--gray-500)' }}>No medical stores available</p>
                        </div>
                    ) : (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
                            {medicals.map((medical, idx) => (
                                <div key={idx} style={{
                                    padding: '1rem',
                                    background: 'var(--gray-50)',
                                    borderRadius: '10px',
                                    border: '1px solid var(--gray-200)'
                                }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                                        <h4 style={{ margin: 0 }}>{medical.name}</h4>
                                        <span className="badge badge-primary">{medical.type}</span>
                                    </div>
                                    <p style={{ fontSize: '0.85rem', color: 'var(--gray-600)', margin: '0.25rem 0' }}>
                                        📍 {medical.address}, {medical.city}
                                    </p>
                                    <p style={{ fontSize: '0.85rem', color: 'var(--gray-600)', margin: '0.25rem 0' }}>
                                        📞 {medical.contact} | ⏰ {medical.hours}
                                    </p>
                                    <div style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                                        <span className="badge badge-success">
                                            {medical.total_medicines || medical.available_medicines?.length || 0} Medicines
                                        </span>
                                        {medical.delivers && <span className="badge badge-warning">Delivery Available</span>}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};








// AI Recommendations Component (Gemini-powered)
const AIRecommendations = () => {
    const { t } = useTranslation();
    const [recommendations, setRecommendations] = useState(null);
    const [loading, setLoading] = useState(false);
    const [question, setQuestion] = useState('');
    const [quickAdvice, setQuickAdvice] = useState('');
    const [askingQuestion, setAskingQuestion] = useState(false);
    const [lastPrediction, setLastPrediction] = useState(null);
    const { getToken } = useAuth();

    useEffect(() => {
        fetchLastPrediction();
    }, []);

    const fetchLastPrediction = async () => {
        try {
            const res = await axios.get(`${API_URL}/hybrid/history`, {
                headers: { Authorization: `Bearer ${getToken()}` }
            });
            if (res.data.success && res.data.predictions?.length > 0) {
                setLastPrediction(res.data.predictions[0]);
            }
        } catch (error) {
            console.error('Failed to fetch prediction history');
        }
    };

    const getAIRecommendations = async () => {
        if (!lastPrediction) {
            toast.error('Please take a CKD test first to get personalized recommendations');
            return;
        }
        setLoading(true);
        try {
            const res = await axios.post(`${API_URL}/gemini/personalized-recommendations`,
                {
                    patient_data: {
                        age: lastPrediction.input_data?.age,
                        weight: lastPrediction.input_data?.weight || 70,
                        input_data: lastPrediction.input_data
                    },
                    prediction_result: lastPrediction.prediction
                },
                { headers: { Authorization: `Bearer ${getToken()}` } }
            );
            if (res.data.success) {
                setRecommendations(res.data.recommendations);
                toast.success('AI recommendations generated!');
            }
        } catch (error) {
            toast.error('Failed to get AI recommendations');
        } finally {
            setLoading(false);
        }
    };

    const askQuestion = async () => {
        if (!question.trim()) {
            toast.error('Please enter a question');
            return;
        }
        setAskingQuestion(true);
        try {
            const res = await axios.post(`${API_URL}/gemini/quick-advice`,
                {
                    question: question,
                    include_medicines: true,  // Enable medicine recommendations
                    context: lastPrediction ? {
                        prediction: lastPrediction.prediction?.result,
                        risk_level: lastPrediction.prediction?.risk_level,
                        age: lastPrediction.input_data?.age,
                        gender: lastPrediction.input_data?.gender || 'unknown',
                        has_diabetes: lastPrediction.input_data?.dm === 'yes',
                        has_hypertension: lastPrediction.input_data?.htn === 'yes',
                        hemoglobin: lastPrediction.input_data?.hemo,
                        serum_creatinine: lastPrediction.input_data?.sc
                    } : {}
                },
                { headers: { Authorization: `Bearer ${getToken()}` } }
            );
            if (res.data.success) {
                setQuickAdvice(res.data.advice);
            }
        } catch (error) {
            toast.error('Failed to get advice');
        } finally {
            setAskingQuestion(false);
        }
    };

    return (
        <div className="page-content animate-fadeIn">
            <div className="page-header">
                <h1>🤖 {t('patient.recommendations.aiTitle')}</h1>
                <p>{t('patient.recommendations.aiSubtitle')}</p>
            </div>

            {/* Quick Question Box */}
            <div className="card" style={{ marginBottom: '2rem', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                <h3 style={{ marginBottom: '1rem', color: 'white' }}>{t('patient.recommendations.askTitle')}</h3>
                <p style={{ marginBottom: '1rem', opacity: 0.9, fontSize: '0.9rem' }}>
                    {t('patient.recommendations.askSubtitle')}
                </p>
                <div className="flex gap-3" style={{ flexWrap: 'wrap' }}>
                    <input
                        type="text"
                        className="form-input"
                        placeholder={t('patient.recommendations.askPlaceholder')}
                        value={question}
                        onChange={e => setQuestion(e.target.value)}
                        onKeyPress={e => e.key === 'Enter' && askQuestion()}
                        style={{ flex: '1', minWidth: '200px', background: 'rgba(255,255,255,0.95)', color: '#333' }}
                    />
                    <button className="btn" onClick={askQuestion} disabled={askingQuestion} style={{ background: 'white', color: '#764ba2', fontWeight: '600' }}>
                        {askingQuestion ? <FaSpinner className="spin" /> : t('patient.recommendations.askButton')}
                    </button>
                </div>
                {quickAdvice && (
                    <div style={{ marginTop: '1.5rem', padding: '1.5rem', background: 'rgba(255,255,255,0.98)', borderRadius: '0.75rem', color: '#333', boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}>
                        <h4 style={{ marginBottom: '0.75rem', color: '#764ba2' }}>{t('patient.recommendations.adviceTitle')}</h4>
                        <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.8', fontSize: '0.95rem' }}><DynamicText text={quickAdvice} /></div>
                        <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#fff3cd', borderRadius: '0.5rem', fontSize: '0.85rem' }}>
                            ⚠️ <strong>{t('patient.recommendations.disclaimer')}</strong>
                        </div>
                    </div>
                )}
            </div>

            {/* Get Personalized Recommendations */}
            <div className="card" style={{ marginBottom: '2rem' }}>
                <h3 style={{ marginBottom: '1rem' }}>{t('patient.recommendations.carePlanTitle')}</h3>
                {lastPrediction ? (
                    <div>
                        <p style={{ marginBottom: '1rem' }}>{t('patient.recommendations.basedOn')} ({lastPrediction.prediction?.result === 'ckd' ? t('patient.ckdDetected') : t('patient.noCkdDetected')}, {t('patient.riskLevel')}: {lastPrediction.prediction?.risk_level})</p>
                        <button className="btn btn-primary btn-lg" onClick={getAIRecommendations} disabled={loading}>
                            {loading ? <><FaSpinner className="spin" /> {t('patient.recommendations.generating')}</> : '🔮 ' + t('patient.aiRecommendations')}
                        </button>
                    </div>
                ) : (
                    <div className="empty-state">
                        <p>{t('patient.recommendations.takeTestFirst')}</p>
                        <Link to="/patient" className="btn btn-primary">{t('patient.recommendations.takeTestButton')}</Link>
                    </div>
                )}
            </div>

            {/* AI Recommendations Display */}
            {recommendations && (
                <div className="recommendations-display">
                    {/* Summary */}
                    <div className="card" style={{ marginBottom: '1rem', borderLeft: '4px solid var(--primary-500)' }}>
                        <h3>📌 {t('patient.recommendations.summary')}</h3>
                        <p style={{ fontSize: '1.1rem', lineHeight: '1.6' }}><DynamicText text={recommendations.summary} /></p>
                        <p><strong>{t('patient.recommendations.estimatedStage')}:</strong> <DynamicText text={recommendations.ckd_stage_assessment} /></p>
                    </div>

                    {/* Diet Recommendations */}
                    {recommendations.diet_recommendations && (
                        <div className="card" style={{ marginBottom: '1rem' }}>
                            <h3>🥗 {t('patient.recommendations.dietTitle')}</h3>
                            <div className="grid grid-cols-2 gap-4" style={{ marginTop: '1rem' }}>
                                <div>
                                    <strong>{t('patient.recommendations.dailyCalories')}:</strong> <DynamicText text={String(recommendations.diet_recommendations.daily_calories)} />
                                </div>
                                <div>
                                    <strong>{t('patient.recommendations.proteinIntake')}:</strong> <DynamicText text={String(recommendations.diet_recommendations.protein_intake)} />
                                </div>
                                <div>
                                    <strong>{t('patient.recommendations.sodiumLimit')}:</strong> <DynamicText text={String(recommendations.diet_recommendations.sodium_limit)} />
                                </div>
                                <div>
                                    <strong>{t('patient.recommendations.fluidIntake')}:</strong> <DynamicText text={String(recommendations.diet_recommendations.fluid_intake)} />
                                </div>
                            </div>
                            <div style={{ marginTop: '1rem' }}>
                                <h4 style={{ color: 'var(--success-600)' }}>✅ {t('patient.recommendations.foodsToEat')}</h4>
                                <ul>{recommendations.diet_recommendations.foods_to_eat?.map((f, i) => <li key={i}><DynamicText text={f} /></li>)}</ul>
                            </div>
                            <div style={{ marginTop: '1rem' }}>
                                <h4 style={{ color: 'var(--error-600)' }}>❌ {t('patient.recommendations.foodsToAvoid')}</h4>
                                <ul>{recommendations.diet_recommendations.foods_to_avoid?.map((f, i) => <li key={i}><DynamicText text={f} /></li>)}</ul>
                            </div>
                        </div>
                    )}

                    {/* Lifestyle Recommendations */}
                    {recommendations.lifestyle_recommendations && (
                        <div className="card" style={{ marginBottom: '1rem' }}>
                            <h3>🏃 {t('patient.recommendations.lifestyleTitle')}</h3>
                            <div style={{ marginTop: '1rem' }}>
                                <h4>{t('patient.recommendations.exercise')}</h4>
                                <p><strong>{t('patient.recommendations.type')}:</strong> <DynamicText text={recommendations.lifestyle_recommendations.exercise?.type} /></p>
                                <p><strong>{t('patient.recommendations.duration')}:</strong> <DynamicText text={recommendations.lifestyle_recommendations.exercise?.duration} /></p>
                                <p><strong>{t('patient.recommendations.precautions')}:</strong> <DynamicText text={recommendations.lifestyle_recommendations.exercise?.precautions} /></p>
                            </div>
                            <p style={{ marginTop: '1rem' }}><strong>{t('patient.recommendations.sleep')}:</strong> <DynamicText text={recommendations.lifestyle_recommendations.sleep} /></p>
                            <p><strong>{t('patient.recommendations.stressManagement')}:</strong> <DynamicText text={recommendations.lifestyle_recommendations.stress_management} /></p>
                        </div>
                    )}

                    {/* Warning Signs */}
                    {recommendations.warning_signs && (
                        <div className="card" style={{ marginBottom: '1rem', borderLeft: '4px solid var(--error-500)' }}>
                            <h3>⚠️ {t('patient.recommendations.warningSigns')}</h3>
                            <ul>{recommendations.warning_signs.map((sign, i) => <li key={i} style={{ color: 'var(--error-600)' }}><DynamicText text={sign} /></li>)}</ul>
                        </div>
                    )}

                    {/* Personalized Tips */}
                    {recommendations.personalized_tips && (
                        <div className="card" style={{ marginBottom: '1rem', background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)' }}>
                            <h3>💡 {t('patient.recommendations.personalizedTips')}</h3>
                            <ul style={{ marginTop: '0.5rem' }}>
                                {recommendations.personalized_tips.map((tip, i) => (
                                    <li key={i} style={{ marginBottom: '0.5rem', padding: '0.5rem', background: 'white', borderRadius: '0.5rem' }}><DynamicText text={tip} /></li>
                                ))}
                            </ul>
                        </div>
                    )}

                    <div style={{ textAlign: 'center', marginTop: '1rem', padding: '1rem', background: '#fff3cd', borderRadius: '0.5rem' }}>
                        <strong>⚠️ {t('patient.recommendations.disclaimer')}</strong>
                    </div>
                </div>
            )}
        </div>
    );
};

// My Appointments Component
const MyAppointments = () => {
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const { getToken } = useAuth();

    useEffect(() => {
        axios.get(`${API_URL}/appointments/my`, { headers: { Authorization: `Bearer ${getToken()}` } })
            .then(res => { if (res.data.success) setAppointments(res.data.appointments); })
            .catch(() => { }).finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="page-content animate-fadeIn">
            <div className="page-header">
                <h1><FaCalendarAlt /> My Appointments</h1>
            </div>
            {appointments.length === 0 ? (
                <div className="empty-state card">
                    <FaCalendarAlt className="empty-icon" />
                    <h3>No Appointments</h3>
                    <Link to="/patient/book" className="btn btn-primary">Book Appointment</Link>
                </div>
            ) : (
                <div className="appointments-grid">
                    {appointments.map((apt) => (
                        <div key={apt._id} className="card appointment-card">
                            <div className="apt-header">
                                <span>{apt.appointment_date} - {apt.appointment_time}</span>
                                <span className={`badge badge-${apt.status === 'confirmed' ? 'success' : 'warning'}`}>{apt.status}</span>
                            </div>
                            <div className="apt-body">
                                <p><FaUserMd /> Dr. {apt.doctor?.name}</p>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

// Book Appointment Component  
const BookAppointment = () => {
    const [doctors, setDoctors] = useState([]);
    const [selectedDoctor, setSelectedDoctor] = useState('');
    const [date, setDate] = useState('');
    const [time, setTime] = useState('');
    const [loading, setLoading] = useState(false);
    const { getToken } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        axios.get(`${API_URL}/doctors`, { headers: { Authorization: `Bearer ${getToken()}` } })
            .then(res => { if (res.data.success) setDoctors(res.data.doctors); })
            .catch(() => { });
    }, []);

    const handleBook = async (e) => {
        e.preventDefault();
        if (!selectedDoctor || !date || !time) { toast.error('Fill all fields'); return; }
        setLoading(true);
        try {
            await axios.post(`${API_URL}/appointments/book`,
                { doctor_id: selectedDoctor, appointment_date: date, appointment_time: time },
                { headers: { Authorization: `Bearer ${getToken()}` } }
            );
            toast.success('Appointment booked!');
            navigate('/patient/appointments');
        } catch (error) {
            toast.error('Booking failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="page-content animate-fadeIn">
            <div className="page-header"><h1><FaCalendarAlt /> Book Appointment</h1></div>
            <div className="card">
                <form onSubmit={handleBook}>
                    <div className="form-group">
                        <label>Select Doctor</label>
                        <select className="form-select" value={selectedDoctor} onChange={e => setSelectedDoctor(e.target.value)}>
                            <option value="">Choose doctor</option>
                            {doctors.map(doc => <option key={doc._id} value={doc._id}>Dr. {doc.name}</option>)}
                        </select>
                    </div>
                    <div className="form-row">
                        <div className="form-group">
                            <label>Date</label>
                            <input type="date" className="form-input" value={date} onChange={e => setDate(e.target.value)} min={new Date().toISOString().split('T')[0]} />
                        </div>
                        <div className="form-group">
                            <label>Time</label>
                            <select className="form-select" value={time} onChange={e => setTime(e.target.value)}>
                                <option value="">Select time</option>
                                <option value="09:00 AM">09:00 AM</option>
                                <option value="10:00 AM">10:00 AM</option>
                                <option value="02:00 PM">02:00 PM</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
                        {loading ? <FaSpinner className="spin" /> : 'Book Appointment'}
                    </button>
                </form>
            </div>
        </div>
    );
};

// ── Patient Profile Component ─────────────────────────────────────
const PatientProfile = () => {
    const { t } = useTranslation();
    const { getToken, user } = useAuth();
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [editMode, setEditMode] = useState(false);
    const [saving, setSaving] = useState(false);
    const [form, setForm] = useState({});

    useEffect(() => { fetchProfile(); }, []);

    const fetchProfile = async () => {
        try {
            const res = await axios.get(`${API_URL}/profile`,
                { headers: { Authorization: `Bearer ${getToken()}` } });
            if (res.data.success) {
                setProfile(res.data.profile);
                setForm({
                    name: res.data.profile.name || '',
                    phone: res.data.profile.phone || '',
                    age: res.data.profile.age || '',
                    gender: res.data.profile.gender || '',
                    blood_group: res.data.profile.blood_group || '',
                    address: res.data.profile.address || '',
                });
            }
        } catch (err) {
            toast.error('Failed to load profile');
        } finally { setLoading(false); }
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            const res = await axios.put(`${API_URL}/profile`, form,
                { headers: { Authorization: `Bearer ${getToken()}` } });
            if (res.data.success) {
                toast.success('Profile updated successfully!');
                setEditMode(false);
                fetchProfile();
            } else {
                toast.error(res.data.message || 'Update failed');
            }
        } catch (err) {
            toast.error('Failed to update profile');
        } finally { setSaving(false); }
    };

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="page-content animate-fadeIn">
            <div className="page-header">
                <h1><FaUser /> My Profile</h1>
                <p>View and update your personal information</p>
            </div>

            <div className="card" style={{ maxWidth: '700px', margin: '0 auto', padding: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{
                            width: '64px', height: '64px', borderRadius: '50%',
                            background: 'linear-gradient(135deg, var(--primary-500), var(--primary-700))',
                            display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '1.75rem'
                        }}><FaUser /></div>
                        <div>
                            <h2 style={{ margin: 0 }}>{profile?.name}</h2>
                            <span style={{ color: 'var(--gray-500)', fontSize: '0.875rem' }}>{profile?.email}</span>
                        </div>
                    </div>
                    {!editMode ? (
                        <button className="btn btn-primary" onClick={() => setEditMode(true)}>✏️ Edit Profile</button>
                    ) : (
                        <div style={{ display: 'flex', gap: '0.75rem' }}>
                            <button className="btn btn-outline" onClick={() => setEditMode(false)}>Cancel</button>
                            <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                                {saving ? '⏳ Saving...' : '💾 Save'}
                            </button>
                        </div>
                    )}
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
                    {[{ label: 'Full Name', field: 'name', type: 'text' }, { label: 'Phone', field: 'phone', type: 'tel' }, { label: 'Age', field: 'age', type: 'number' }, { label: 'Gender', field: 'gender', type: 'select', options: ['Male', 'Female', 'Other'] }, { label: 'Blood Group', field: 'blood_group', type: 'select', options: ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'] }, { label: 'Address', field: 'address', type: 'text', full: true }].map(({ label, field, type, options, full }) => (
                        <div key={field} style={{ gridColumn: full ? '1 / -1' : 'auto' }}>
                            <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.4rem', color: 'var(--gray-600)', fontSize: '0.875rem' }}>{label}</label>
                            {!editMode ? (
                                <div style={{ padding: '0.6rem 0.9rem', background: 'var(--gray-50)', borderRadius: '0.5rem', color: profile?.[field] ? 'var(--gray-800)' : 'var(--gray-400)', border: '1px solid var(--gray-200)' }}>
                                    {profile?.[field] || '—'}
                                </div>
                            ) : type === 'select' ? (
                                <select className="form-select" value={form[field]} onChange={e => setForm({ ...form, [field]: e.target.value })}>
                                    <option value="">Select {label}</option>
                                    {options.map(o => <option key={o} value={o}>{o}</option>)}
                                </select>
                            ) : (
                                <input className="form-input" type={type} value={form[field]} onChange={e => setForm({ ...form, [field]: e.target.value })} placeholder={`Enter ${label}`} />
                            )}
                        </div>
                    ))}
                </div>

                {profile?.created_at && (
                    <p style={{ marginTop: '1.5rem', color: 'var(--gray-400)', fontSize: '0.8rem', textAlign: 'right' }}>
                        Member since: {new Date(profile.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                    </p>
                )}
            </div>
        </div>
    );
};

// Main Patient Dashboard
const PatientDashboard = () => {
    const { t } = useTranslation();
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <div className="dashboard">
            <aside className="sidebar">
                <div className="sidebar-header">
                    <FaHeartbeat className="sidebar-logo" />
                    <span>{t('landing.brand')}</span>
                </div>
                <nav className="sidebar-nav">
                    <Link to="/patient" className="nav-item"><FaFlask /> {t('patient.ckdTest')}</Link>
                    <Link to="/patient/upload-report" className="nav-item">📄 {t('patient.uploadReport')}</Link>
                    <Link to="/patient/history" className="nav-item"><FaHistory /> {t('patient.testHistory')}</Link>
                    <Link to="/patient/ai-recommendations" className="nav-item">🤖 {t('patient.aiRecommendations', 'AI Recommendations')}</Link>
                    <Link to="/patient/telemedicine" className="nav-item"><FaVideo /> {t('patient.telemedicine')}</Link>
                    <Link to="/patient/donor" className="nav-item"><FaHandHoldingHeart /> {t('patient.donorMatch')}</Link>
                    <Link to="/patient/pharmacy" className="nav-item"><FaPills /> {t('patient.pharmacy')}</Link>
                    <Link to="/patient/appointments" className="nav-item"><FaCalendarAlt /> {t('patient.appointments')}</Link>
                    <Link to="/patient/book" className="nav-item"><FaUserMd /> {t('patient.bookDoctor', 'Book Doctor')}</Link>
                    <Link to="/patient/profile" className="nav-item"><FaUser /> My Profile</Link>
                </nav>
                <div className="sidebar-footer">
                    <div className="sidebar-language">
                        <LanguageSwitcher />
                    </div>
                    <div className="user-info">
                        <FaUser className="user-avatar" />
                        <div>
                            <span className="user-name">{user?.name}</span>
                            <span className="user-role">{t('auth.patient')}</span>
                        </div>
                    </div>
                    <button onClick={handleLogout} className="logout-btn"><FaSignOutAlt /> {t('common.logout')}</button>
                </div>
            </aside>

            <main className="main-content">
                <Routes>
                    <Route path="/" element={<CKDTestForm />} />
                    <Route path="/ckd-test" element={<CKDTestForm />} />
                    <Route path="/upload-report" element={<ReportUpload />} />
                    <Route path="/history" element={<CKDTestHistory />} />
                    <Route path="/ai-recommendations" element={<AIRecommendations />} />
                    <Route path="/telemedicine" element={<Telemedicine />} />
                    <Route path="/donor" element={<DonorMatching />} />
                    <Route path="/pharmacy" element={<PharmacyMedicine />} />
                    <Route path="/appointments" element={<MyAppointments />} />
                    <Route path="/book" element={<BookAppointment />} />
                    <Route path="/book/:doctorId" element={<BookAppointment />} />
                    <Route path="/profile" element={<PatientProfile />} />
                </Routes>
            </main>
        </div>
    );
};

export default PatientDashboard;
