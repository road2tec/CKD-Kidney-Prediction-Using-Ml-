import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { FaHeartbeat, FaCalendarAlt, FaHistory, FaSignOutAlt, FaUser, FaFlask, FaFileDownload, FaSpinner, FaCheckCircle, FaExclamationTriangle, FaVideo, FaPills, FaHandHoldingHeart, FaUserMd, FaPhone, FaClinicMedical, FaPhoneAlt } from 'react-icons/fa';
import { toast } from 'react-toastify';
import axios from 'axios';
import { saveAs } from 'file-saver';
import { useAuth, API_URL } from '../App';
import './Dashboard.css';
import CKDTestForm from './CKDTestForm';
import ReportUpload from './ReportUpload';
import VideoCall from '../components/VideoCall';


// CKD Test History Component
const CKDTestHistory = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const { getToken } = useAuth();

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
                <h1><FaHistory /> CKD Test History</h1>
                <p>View your past CKD screening results and download reports</p>
            </div>
            {history.length === 0 ? (
                <div className="empty-state card">
                    <FaFlask className="empty-icon" />
                    <h3>No CKD Tests Yet</h3>
                    <p>Take your first CKD screening test to get started</p>
                    <Link to="/patient" className="btn btn-primary">Take CKD Test</Link>
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
                                        <h3>{record.prediction?.result === 'ckd' ? 'CKD Detected' : 'No CKD Detected'}</h3>
                                        <span className="history-date">{formatDate(record.timestamp)}</span>
                                    </div>
                                </div>
                                <span className={`badge ${record.prediction?.risk_level === 'High' ? 'badge-error' : 'badge-success'}`}>
                                    {record.prediction?.risk_level || 'N/A'} Risk
                                </span>
                            </div>
                            <div className="history-body">
                                <div className="history-metrics">
                                    <div className="metric-item">
                                        <span className="metric-label">Confidence</span>
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
                                    <FaFileDownload /> Download PDF
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

// Telemedicine Component
const Telemedicine = () => {
    const [sessions, setSessions] = useState([]);
    const [slots, setSlots] = useState([]);
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
                <h1><FaVideo /> Telemedicine Consultation</h1>
                <p>Book video/audio consultations with CKD specialists</p>
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
                <h3 style={{ marginBottom: '1rem' }}>My Scheduled Sessions</h3>
                {sessions.length === 0 ? (
                    <p style={{ color: 'var(--gray-500)' }}>No scheduled sessions. Book a consultation above.</p>
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
                                        {session.status}
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
                <h1><FaHandHoldingHeart /> Donor-Patient Matching</h1>
                <p>Register as a kidney donor or find compatible donors</p>
            </div>

            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-value">{stats.total_registered_donors || 0}</div>
                    <div className="stat-label">Registered Donors</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{stats.available_donors || 0}</div>
                    <div className="stat-label">Available</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{stats.successful_matches || 0}</div>
                    <div className="stat-label">Successful Matches</div>
                </div>
            </div>

            <div className="card" style={{ marginTop: '2rem' }}>
                <h3>Your Donor Status</h3>
                {donorProfile ? (
                    <div className="donor-profile">
                        <p><strong>Blood Group:</strong> {donorProfile.blood_group}</p>
                        <p><strong>Status:</strong> <span className={`badge ${donorProfile.is_available ? 'badge-success' : 'badge-warning'}`}>
                            {donorProfile.is_available ? 'Available' : 'Unavailable'}
                        </span></p>
                        <p><strong>Registered:</strong> {donorProfile.registration_date ? new Date(donorProfile.registration_date).toLocaleDateString() : 'N/A'}</p>
                    </div>
                ) : (
                    <div>
                        <p style={{ marginBottom: '1rem' }}>You are not registered as a donor yet.</p>
                        {!showRegister ? (
                            <button className="btn btn-primary" onClick={() => setShowRegister(true)}>
                                <FaHandHoldingHeart /> Register as Donor
                            </button>
                        ) : (
                            <div className="donor-form">
                                <div className="form-row">
                                    <select className="form-select" value={formData.blood_group} onChange={e => setFormData({ ...formData, blood_group: e.target.value })}>
                                        <option value="">Blood Group</option>
                                        <option value="A+">A+</option><option value="A-">A-</option>
                                        <option value="B+">B+</option><option value="B-">B-</option>
                                        <option value="AB+">AB+</option><option value="AB-">AB-</option>
                                        <option value="O+">O+</option><option value="O-">O-</option>
                                    </select>
                                    <input className="form-input" type="number" placeholder="Age" value={formData.age} onChange={e => setFormData({ ...formData, age: e.target.value })} />
                                </div>
                                <div className="form-row">
                                    <input className="form-input" type="number" placeholder="Weight (kg)" value={formData.weight} onChange={e => setFormData({ ...formData, weight: e.target.value })} />
                                    <input className="form-input" type="tel" placeholder="Contact Phone" value={formData.contact_phone} onChange={e => setFormData({ ...formData, contact_phone: e.target.value })} />
                                </div>
                                <button className="btn btn-primary" onClick={registerAsDonor}>Submit Registration</button>
                            </div>
                        )}
                    </div>
                )}
            </div>

            <div className="card" style={{ marginTop: '2rem' }}>
                <h3>Find Compatible Donors</h3>
                <button className="btn btn-outline" onClick={findMatches} style={{ marginBottom: '1rem' }}>
                    Search for Matches
                </button>
                {matches.length > 0 && (
                    <div className="matches-list">
                        {matches.map((match, idx) => (
                            <div key={idx} className="match-item" style={{ flexDirection: 'column', alignItems: 'flex-start', padding: '1.5rem', borderBottom: '1px solid #eee' }}>
                                <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                    <div>
                                        <h4 style={{ margin: 0, fontSize: '1.1rem', color: 'var(--primary-700)' }}>
                                            Blood Group: {match.blood_group}
                                        </h4>
                                        <span style={{ fontSize: '0.85rem', color: 'var(--gray-500)' }}>Age: {match.age} years ({match.age_difference} yr gap)</span>
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
                                            {match.compatibility_score}% Compatible
                                        </div>
                                    </div>
                                </div>

                                <div className="match-reasons" style={{ background: '#f8fafc', padding: '1rem', borderRadius: '0.5rem', width: '100%' }}>
                                    <h5 style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem', color: 'var(--gray-600)' }}>Compatibility Breakdown:</h5>
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

// Pharmacy & Medicine Component with Search
const PharmacyMedicine = () => {
    const [medications, setMedications] = useState({});
    const [pharmacies, setPharmacies] = useState([]);
    const [searchResults, setSearchResults] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchType, setSearchType] = useState('medicines'); // 'medicines' or 'pharmacies'
    const [loading, setLoading] = useState(true);
    const [searching, setSearching] = useState(false);
    const [categories, setCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const { getToken } = useAuth();

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [medsRes, pharmaRes, catsRes] = await Promise.all([
                axios.get(`${API_URL}/pharmacy/medications`),
                axios.get(`${API_URL}/pharmacy/pharmacies`),
                axios.get(`${API_URL}/pharmacy/categories`)
            ]);
            if (medsRes.data.success) setMedications(medsRes.data.medications || {});
            if (pharmaRes.data.success) setPharmacies(pharmaRes.data.pharmacies || []);
            if (catsRes.data.success) setCategories(catsRes.data.categories || []);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async () => {
        if (!searchQuery.trim()) {
            setSearchResults(null);
            return;
        }
        setSearching(true);
        try {
            const endpoint = searchType === 'medicines'
                ? `${API_URL}/pharmacy/search/medicines?q=${encodeURIComponent(searchQuery)}${selectedCategory ? `&category=${selectedCategory}` : ''}`
                : `${API_URL}/pharmacy/search/pharmacies?q=${encodeURIComponent(searchQuery)}`;
            const res = await axios.get(endpoint);
            if (res.data.success) {
                setSearchResults(searchType === 'medicines' ? res.data.medicines : res.data.pharmacies);
            }
        } catch (error) {
            toast.error('Search failed');
        } finally {
            setSearching(false);
        }
    };

    const clearSearch = () => {
        setSearchQuery('');
        setSearchResults(null);
        setSelectedCategory('');
    };

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="page-content animate-fadeIn">
            <div className="page-header">
                <h1><FaPills /> Pharmacy & Medicines</h1>
                <p>Search CKD medications and find nearby pharmacies</p>
            </div>

            {/* Search Section */}
            <div className="card" style={{ marginBottom: '2rem' }}>
                <h3 style={{ marginBottom: '1rem' }}>🔍 Search Medicines & Pharmacies</h3>
                <div className="flex gap-3 mb-4" style={{ flexWrap: 'wrap' }}>
                    <div className="filter-tabs" style={{ marginBottom: 0 }}>
                        <button className={`filter-tab ${searchType === 'medicines' ? 'active' : ''}`} onClick={() => { setSearchType('medicines'); clearSearch(); }}>Medicines</button>
                        <button className={`filter-tab ${searchType === 'pharmacies' ? 'active' : ''}`} onClick={() => { setSearchType('pharmacies'); clearSearch(); }}>Pharmacies</button>
                    </div>
                </div>
                <div className="flex gap-3" style={{ flexWrap: 'wrap' }}>
                    <input
                        type="text"
                        className="form-input"
                        placeholder={searchType === 'medicines' ? 'Search medicine name, purpose...' : 'Search pharmacy name, city...'}
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                        onKeyPress={e => e.key === 'Enter' && handleSearch()}
                        style={{ flex: '1', minWidth: '200px' }}
                    />
                    {searchType === 'medicines' && (
                        <select className="form-select" value={selectedCategory} onChange={e => setSelectedCategory(e.target.value)} style={{ width: 'auto' }}>
                            <option value="">All Categories</option>
                            {categories.map(cat => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
                        </select>
                    )}
                    <button className="btn btn-primary" onClick={handleSearch} disabled={searching}>
                        {searching ? <FaSpinner className="spin" /> : 'Search'}
                    </button>
                    {searchResults && <button className="btn btn-secondary" onClick={clearSearch}>Clear</button>}
                </div>
            </div>

            {/* Search Results */}
            {searchResults && (
                <div className="card" style={{ marginBottom: '2rem' }}>
                    <h3 style={{ marginBottom: '1rem' }}>Search Results ({searchResults.length})</h3>
                    {searchResults.length === 0 ? (
                        <p style={{ color: 'var(--gray-500)' }}>No results found for "{searchQuery}"</p>
                    ) : searchType === 'medicines' ? (
                        <div className="med-categories">
                            {searchResults.map((med, idx) => (
                                <div key={idx} className="med-category" style={{ flexBasis: '100%', maxWidth: '100%' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                                        <h4 style={{ margin: 0 }}>{med.name}</h4>
                                        <div className="flex gap-2">
                                            <span className={`badge ${med.ckd_relevance === 'High' ? 'badge-error' : med.ckd_relevance === 'Medium' ? 'badge-warning' : 'badge-success'}`}>{med.ckd_relevance} CKD Relevance</span>
                                            <span className={`badge ${med.requires_prescription ? 'badge-warning' : 'badge-success'}`}>{med.requires_prescription ? 'Rx Required' : 'OTC'}</span>
                                        </div>
                                    </div>
                                    <p><strong>Purpose:</strong> {med.purpose}</p>
                                    <p><strong>Category:</strong> {med.category_name}</p>
                                    {med.notes && <p><strong>Notes:</strong> {med.notes}</p>}
                                    <p><strong>Price Range:</strong> {med.price_range || 'N/A'}</p>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="pharmacy-list">
                            {searchResults.map((pharmacy, idx) => (
                                <div key={idx} className="pharmacy-item">
                                    <div className="pharmacy-info">
                                        <h4>{pharmacy.name}</h4>
                                        <p>{pharmacy.address}, {pharmacy.city}</p>
                                        <p>{pharmacy.hours} | {pharmacy.contact}</p>
                                        {pharmacy.rating && <p>⭐ {pharmacy.rating}/5</p>}
                                    </div>
                                    <div className="pharmacy-badges">
                                        {pharmacy.delivers && <span className="badge badge-success">Delivery</span>}
                                        <span className="badge badge-primary">{pharmacy.type}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Default Content - Show when not searching */}
            {!searchResults && (
                <>
                    <div className="card">
                        <h3 style={{ marginBottom: '1rem' }}>CKD Medication Categories</h3>
                        <div className="med-categories">
                            {Object.entries(medications).map(([key, category]) => (
                                <div key={key} className="med-category">
                                    <h4>{category.category}</h4>
                                    <ul>
                                        {category.medications?.slice(0, 3).map((med, idx) => (
                                            <li key={idx}>
                                                <strong>{med.name}</strong>
                                                <span>{med.purpose}</span>
                                                {med.price_range && <small style={{ color: 'var(--gray-500)' }}>{med.price_range}</small>}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="card" style={{ marginTop: '2rem' }}>
                        <h3 style={{ marginBottom: '1rem' }}><FaClinicMedical /> Nearby Pharmacies</h3>
                        {pharmacies.length === 0 ? (
                            <p style={{ color: 'var(--gray-500)' }}>No pharmacies found nearby.</p>
                        ) : (
                            <div className="pharmacy-list">
                                {pharmacies.map((pharmacy, idx) => (
                                    <div key={idx} className="pharmacy-item">
                                        <div className="pharmacy-info">
                                            <h4>{pharmacy.name}</h4>
                                            <p>{pharmacy.address ? `${pharmacy.address}` : `${pharmacy.distance} away`}</p>
                                            <p style={{ fontSize: '0.85rem', color: 'var(--gray-500)' }}>
                                                {pharmacy.city}{pharmacy.state ? `, ${pharmacy.state}` : ''}{pharmacy.pincode ? ` - ${pharmacy.pincode}` : ''}
                                            </p>
                                            <p><FaPhoneAlt style={{ marginRight: '4px' }} />{pharmacy.contact} | {pharmacy.hours}</p>
                                            {pharmacy.rating && <p>⭐ {pharmacy.rating}/5</p>}
                                        </div>
                                        <div className="pharmacy-badges">
                                            {pharmacy.delivers && <span className="badge badge-success">Delivery</span>}
                                            <span className="badge badge-primary">{pharmacy.type}</span>
                                            {(pharmacy.total_medicines || pharmacy.available_medicines?.length > 0) && (
                                                <span className="badge badge-warning">{pharmacy.total_medicines || pharmacy.available_medicines?.length} medicines</span>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </>
            )}
        </div>
    );
};

// AI Recommendations Component (Gemini-powered)
const AIRecommendations = () => {
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
                <h1>🤖 AI Health Recommendations</h1>
                <p>Personalized treatment and lifestyle recommendations powered by Google Gemini AI</p>
            </div>

            {/* Quick Question Box */}
            <div className="card" style={{ marginBottom: '2rem', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                <h3 style={{ marginBottom: '1rem', color: 'white' }}>💬 Ask AI About Your Health & Medicines</h3>
                <p style={{ marginBottom: '1rem', opacity: 0.9, fontSize: '0.9rem' }}>
                    Get personalized health advice including medicine recommendations based on your profile
                </p>
                <div className="flex gap-3" style={{ flexWrap: 'wrap' }}>
                    <input
                        type="text"
                        className="form-input"
                        placeholder="e.g., What medicines help with CKD? What should I avoid with high creatinine?"
                        value={question}
                        onChange={e => setQuestion(e.target.value)}
                        onKeyPress={e => e.key === 'Enter' && askQuestion()}
                        style={{ flex: '1', minWidth: '200px', background: 'rgba(255,255,255,0.95)', color: '#333' }}
                    />
                    <button className="btn" onClick={askQuestion} disabled={askingQuestion} style={{ background: 'white', color: '#764ba2', fontWeight: '600' }}>
                        {askingQuestion ? <FaSpinner className="spin" /> : '🤖 Ask AI'}
                    </button>
                </div>
                {quickAdvice && (
                    <div style={{ marginTop: '1.5rem', padding: '1.5rem', background: 'rgba(255,255,255,0.98)', borderRadius: '0.75rem', color: '#333', boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}>
                        <h4 style={{ marginBottom: '0.75rem', color: '#764ba2' }}>💊 AI Health & Medicine Advice</h4>
                        <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.8', fontSize: '0.95rem' }}>{quickAdvice}</div>
                        <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#fff3cd', borderRadius: '0.5rem', fontSize: '0.85rem' }}>
                            ⚠️ <strong>Disclaimer:</strong> This AI-generated advice is for informational purposes only. Always consult your doctor before taking any medication or making health decisions.
                        </div>
                    </div>
                )}
            </div>

            {/* Get Personalized Recommendations */}
            <div className="card" style={{ marginBottom: '2rem' }}>
                <h3 style={{ marginBottom: '1rem' }}>📋 Personalized CKD Care Plan</h3>
                {lastPrediction ? (
                    <div>
                        <p style={{ marginBottom: '1rem' }}>Based on your last CKD test ({lastPrediction.prediction?.result === 'ckd' ? 'CKD Detected' : 'No CKD'}, {lastPrediction.prediction?.risk_level} Risk)</p>
                        <button className="btn btn-primary btn-lg" onClick={getAIRecommendations} disabled={loading}>
                            {loading ? <><FaSpinner className="spin" /> Generating...</> : '🔮 Get AI Recommendations'}
                        </button>
                    </div>
                ) : (
                    <div className="empty-state">
                        <p>Take a CKD test first to get personalized AI recommendations</p>
                        <Link to="/patient" className="btn btn-primary">Take CKD Test</Link>
                    </div>
                )}
            </div>

            {/* AI Recommendations Display */}
            {recommendations && (
                <div className="recommendations-display">
                    {/* Summary */}
                    <div className="card" style={{ marginBottom: '1rem', borderLeft: '4px solid var(--primary-500)' }}>
                        <h3>📌 Summary</h3>
                        <p style={{ fontSize: '1.1rem', lineHeight: '1.6' }}>{recommendations.summary}</p>
                        <p><strong>Estimated CKD Stage:</strong> {recommendations.ckd_stage_assessment}</p>
                    </div>

                    {/* Diet Recommendations */}
                    {recommendations.diet_recommendations && (
                        <div className="card" style={{ marginBottom: '1rem' }}>
                            <h3>🥗 Diet Recommendations</h3>
                            <div className="grid grid-cols-2 gap-4" style={{ marginTop: '1rem' }}>
                                <div>
                                    <strong>Daily Calories:</strong> {recommendations.diet_recommendations.daily_calories}
                                </div>
                                <div>
                                    <strong>Protein Intake:</strong> {recommendations.diet_recommendations.protein_intake}
                                </div>
                                <div>
                                    <strong>Sodium Limit:</strong> {recommendations.diet_recommendations.sodium_limit}
                                </div>
                                <div>
                                    <strong>Fluid Intake:</strong> {recommendations.diet_recommendations.fluid_intake}
                                </div>
                            </div>
                            <div style={{ marginTop: '1rem' }}>
                                <h4 style={{ color: 'var(--success-600)' }}>✅ Foods to Eat</h4>
                                <ul>{recommendations.diet_recommendations.foods_to_eat?.map((f, i) => <li key={i}>{f}</li>)}</ul>
                            </div>
                            <div style={{ marginTop: '1rem' }}>
                                <h4 style={{ color: 'var(--error-600)' }}>❌ Foods to Avoid</h4>
                                <ul>{recommendations.diet_recommendations.foods_to_avoid?.map((f, i) => <li key={i}>{f}</li>)}</ul>
                            </div>
                        </div>
                    )}

                    {/* Lifestyle Recommendations */}
                    {recommendations.lifestyle_recommendations && (
                        <div className="card" style={{ marginBottom: '1rem' }}>
                            <h3>🏃 Lifestyle Recommendations</h3>
                            <div style={{ marginTop: '1rem' }}>
                                <h4>Exercise</h4>
                                <p><strong>Type:</strong> {recommendations.lifestyle_recommendations.exercise?.type}</p>
                                <p><strong>Duration:</strong> {recommendations.lifestyle_recommendations.exercise?.duration}</p>
                                <p><strong>Precautions:</strong> {recommendations.lifestyle_recommendations.exercise?.precautions}</p>
                            </div>
                            <p style={{ marginTop: '1rem' }}><strong>Sleep:</strong> {recommendations.lifestyle_recommendations.sleep}</p>
                            <p><strong>Stress Management:</strong> {recommendations.lifestyle_recommendations.stress_management}</p>
                        </div>
                    )}

                    {/* Warning Signs */}
                    {recommendations.warning_signs && (
                        <div className="card" style={{ marginBottom: '1rem', borderLeft: '4px solid var(--error-500)' }}>
                            <h3>⚠️ Warning Signs to Watch</h3>
                            <ul>{recommendations.warning_signs.map((sign, i) => <li key={i} style={{ color: 'var(--error-600)' }}>{sign}</li>)}</ul>
                        </div>
                    )}

                    {/* Personalized Tips */}
                    {recommendations.personalized_tips && (
                        <div className="card" style={{ marginBottom: '1rem', background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)' }}>
                            <h3>💡 Personalized Tips for You</h3>
                            <ul style={{ marginTop: '0.5rem' }}>
                                {recommendations.personalized_tips.map((tip, i) => (
                                    <li key={i} style={{ marginBottom: '0.5rem', padding: '0.5rem', background: 'white', borderRadius: '0.5rem' }}>{tip}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    <div style={{ textAlign: 'center', marginTop: '1rem', padding: '1rem', background: '#fff3cd', borderRadius: '0.5rem' }}>
                        <strong>⚠️ Disclaimer:</strong> These are AI-generated recommendations for informational purposes only. Always consult your healthcare provider before making any changes to your treatment or lifestyle.
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

// Main Patient Dashboard
const PatientDashboard = () => {
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
                    <span>CKD System</span>
                </div>
                <nav className="sidebar-nav">
                    <Link to="/patient" className="nav-item"><FaFlask /> CKD Test</Link>
                    <Link to="/patient/upload-report" className="nav-item">📄 Upload Report</Link>
                    <Link to="/patient/history" className="nav-item"><FaHistory /> Test History</Link>
                    <Link to="/patient/ai-recommendations" className="nav-item">🤖 AI Recommendations</Link>
                    <Link to="/patient/telemedicine" className="nav-item"><FaVideo /> Telemedicine</Link>
                    <Link to="/patient/donor" className="nav-item"><FaHandHoldingHeart /> Donor Matching</Link>
                    <Link to="/patient/pharmacy" className="nav-item"><FaPills /> Pharmacy</Link>
                    <Link to="/patient/appointments" className="nav-item"><FaCalendarAlt /> Appointments</Link>
                    <Link to="/patient/book" className="nav-item"><FaUserMd /> Book Doctor</Link>
                </nav>
                <div className="sidebar-footer">
                    <div className="user-info">
                        <FaUser className="user-avatar" />
                        <div>
                            <span className="user-name">{user?.name}</span>
                            <span className="user-role">Patient</span>
                        </div>
                    </div>
                    <button onClick={handleLogout} className="logout-btn"><FaSignOutAlt /> Logout</button>
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
                </Routes>
            </main>
        </div>
    );
};

export default PatientDashboard;
