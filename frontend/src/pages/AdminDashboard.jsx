import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { FaHeartbeat, FaUsers, FaUserMd, FaCalendarAlt, FaChartBar, FaSignOutAlt, FaUserShield, FaPlus, FaTrash, FaSpinner, FaPills } from 'react-icons/fa';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useAuth, API_URL } from '../App';
import './Dashboard.css';
import LanguageSwitcher from '../components/LanguageSwitcher';

// Stats Overview
const AdminOverview = () => {
    const { t } = useTranslation();
    const [stats, setStats] = useState(null);
    const { getToken } = useAuth();

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await axios.get(`${API_URL}/admin/stats`, { headers: { Authorization: `Bearer ${getToken()}` } });
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
                <h1><FaChartBar /> {t('admin.dashboard')}</h1>
                <p>{t('admin.systemOverview')}</p>
            </div>

            <div className="stats-grid">
                <div className="card stat-card">
                    <div className="stat-icon blue"><FaUsers /></div>
                    <div className="stat-info"><h3>{stats.patients}</h3><p>{t('admin.patients')}</p></div>
                </div>
                <div className="card stat-card">
                    <div className="stat-icon green"><FaUserMd /></div>
                    <div className="stat-info"><h3>{stats.doctors}</h3><p>{t('admin.doctors')}</p></div>
                </div>
                <div className="card stat-card">
                    <div className="stat-icon orange"><FaCalendarAlt /></div>
                    <div className="stat-info"><h3>{stats.appointments}</h3><p>{t('admin.appointments')}</p></div>
                </div>
                <div className="card stat-card">
                    <div className="stat-icon purple"><FaChartBar /></div>
                    <div className="stat-info"><h3>{stats.predictions}</h3><p>{t('admin.aiPredictions')}</p></div>
                </div>
            </div>

            <div className="grid grid-cols-2 mt-6">
                <div className="card">
                    <h3>{t('doctor.quickActions')}</h3>
                    <div className="flex flex-col gap-3 mt-4">
                        <Link to="/admin/doctors" className="btn btn-primary">{t('admin.manageDoctors')}</Link>
                        <Link to="/admin/users" className="btn btn-secondary">{t('admin.viewAllUsers')}</Link>
                        <Link to="/admin/appointments" className="btn btn-secondary">{t('admin.viewAppointments')}</Link>
                    </div>
                </div>
                <div className="card">
                    <h3>{t('admin.systemInfo')}</h3>
                    <div className="mt-4">
                        <p><strong>{t('admin.database')}:</strong> MongoDB (missing_person)</p>
                        <p><strong>{t('admin.mlModel')}:</strong> Multinomial Naive Bayes</p>
                        <p><strong>{t('admin.status')}:</strong> <span className="badge badge-success">{t('admin.active')}</span></p>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Users Management
const UsersManagement = () => {
    const { t } = useTranslation();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const { getToken } = useAuth();

    useEffect(() => { fetchUsers(); }, [filter]);

    const fetchUsers = async () => {
        try {
            const url = filter === 'all' ? `${API_URL}/admin/users` : `${API_URL}/admin/users?role=${filter}`;
            const response = await axios.get(url, { headers: { Authorization: `Bearer ${getToken()}` } });
            if (response.data.success) setUsers(response.data.users);
        } catch (error) {
            toast.error('Failed to fetch users');
        } finally {
            setLoading(false);
        }
    };

    const deleteUser = async (id) => {
        if (!window.confirm('Deactivate this user?')) return;
        try {
            const response = await axios.delete(`${API_URL}/admin/delete-user/${id}`, { headers: { Authorization: `Bearer ${getToken()}` } });
            if (response.data.success) { toast.success('User deactivated'); fetchUsers(); }
        } catch (error) {
            toast.error('Failed to deactivate user');
        }
    };

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="page-content animate-fadeIn">
            <div className="page-header">
                <h1><FaUsers /> {t('admin.usersManagement')}</h1>
                <p>{t('admin.viewManageUsers')}</p>
            </div>

            <div className="filter-tabs mb-4">
                {['all', 'patient', 'doctor', 'admin'].map(f => (
                    <button key={f} className={`filter-tab ${filter === f ? 'active' : ''}`} onClick={() => setFilter(f)}>
                        {f.charAt(0).toUpperCase() + f.slice(1)}s
                    </button>
                ))}
            </div>

            <div className="table-container card">
                <table className="data-table">
                    <thead>
                        <tr><th>{t('admin.name')}</th><th>{t('admin.email')}</th><th>{t('admin.role')}</th><th>{t('admin.status')}</th><th>{t('admin.actions')}</th></tr>
                    </thead>
                    <tbody>
                        {users.map(user => (
                            <tr key={user._id}>
                                <td><strong>{user.name}</strong></td>
                                <td>{user.email}</td>
                                <td><span className={`badge badge-${user.role === 'admin' ? 'error' : user.role === 'doctor' ? 'success' : 'primary'}`}>{user.role}</span></td>
                                <td><span className={`badge ${user.is_active !== false ? 'badge-success' : 'badge-error'}`}>{user.is_active !== false ? t('admin.active') : t('admin.inactive')}</span></td>
                                <td>
                                    {user.role !== 'admin' && (
                                        <button className="btn btn-sm btn-danger" onClick={() => deleteUser(user._id)}><FaTrash /></button>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

// Doctor Management
const DoctorManagement = () => {
    const { t } = useTranslation();
    const [doctors, setDoctors] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [loading, setLoading] = useState(true);
    const [formData, setFormData] = useState({ name: '', email: '', password: '', specialization: '', phone: '', experience: '', consultation_fee: '' });
    const { getToken } = useAuth();

    useEffect(() => { fetchDoctors(); }, []);

    const fetchDoctors = async () => {
        try {
            const response = await axios.get(`${API_URL}/admin/doctors`, { headers: { Authorization: `Bearer ${getToken()}` } });
            if (response.data.success) setDoctors(response.data.doctors);
        } catch (error) {
            toast.error('Failed to fetch doctors');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post(`${API_URL}/admin/add-doctor`, formData, { headers: { Authorization: `Bearer ${getToken()}` } });
            if (response.data.success) {
                toast.success('Doctor added successfully');
                setShowForm(false);
                setFormData({ name: '', email: '', password: '', specialization: '', phone: '', experience: '', consultation_fee: '' });
                fetchDoctors();
            }
        } catch (error) {
            toast.error(error.response?.data?.message || 'Failed to add doctor');
        }
    };

    const specializations = ['General Physician', 'Cardiologist', 'Dermatologist', 'Neurologist', 'Gastroenterologist', 'Pulmonologist', 'Endocrinologist', 'Orthopedic', 'Urologist', 'Proctologist', 'Infectious Disease Specialist'];

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="page-content animate-fadeIn">
            <div className="page-header flex justify-between items-center">
                <div><h1><FaUserMd /> {t('admin.doctorManagement')}</h1><p>{t('admin.manageDoctorsDesc')}</p></div>
                <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}><FaPlus /> {t('admin.addDoctor')}</button>
            </div>

            {showForm && (
                <div className="card mb-6 animate-fadeIn">
                    <h3 className="mb-4">{t('admin.createNewDoctor')}</h3>
                    <form onSubmit={handleSubmit}>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="form-group">
                                <label className="form-label">{t('admin.name')} *</label>
                                <input type="text" className="form-input" value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} required />
                            </div>
                            <div className="form-group">
                                <label className="form-label">{t('admin.email')} *</label>
                                <input type="email" className="form-input" value={formData.email} onChange={e => setFormData({ ...formData, email: e.target.value })} required />
                            </div>
                            <div className="form-group">
                                <label className="form-label">{t('admin.password')} *</label>
                                <input type="password" className="form-input" value={formData.password} onChange={e => setFormData({ ...formData, password: e.target.value })} required />
                            </div>
                            <div className="form-group">
                                <label className="form-label">{t('admin.specialization')} *</label>
                                <select className="form-select" value={formData.specialization} onChange={e => setFormData({ ...formData, specialization: e.target.value })} required>
                                    <option value="">{t('admin.select')}</option>
                                    {specializations.map(s => <option key={s} value={s}>{s}</option>)}
                                </select>
                            </div>
                            <div className="form-group">
                                <label className="form-label">{t('admin.phone')}</label>
                                <input type="tel" className="form-input" value={formData.phone} onChange={e => setFormData({ ...formData, phone: e.target.value })} />
                            </div>
                            <div className="form-group">
                                <label className="form-label">{t('admin.experience')}</label>
                                <input type="text" className="form-input" placeholder="e.g., 5 years" value={formData.experience} onChange={e => setFormData({ ...formData, experience: e.target.value })} />
                            </div>
                        </div>
                        <div className="flex gap-3 mt-4">
                            <button type="submit" className="btn btn-primary">{t('admin.addDoctor')}</button>
                            <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>{t('admin.cancel')}</button>
                        </div>
                    </form>
                </div>
            )}

            <div className="doctors-grid">
                {doctors.map(doc => (
                    <div key={doc._id} className="card doctor-admin-card">
                        <div className="doc-header">
                            <div className="doc-avatar"><FaUserMd /></div>
                            <div>
                                <h4>Dr. {doc.name}</h4>
                                <p className="text-primary">{doc.specialization}</p>
                            </div>
                            <span className={`badge ${doc.is_active !== false ? 'badge-success' : 'badge-error'}`}>{doc.is_active !== false ? t('admin.active') : t('admin.inactive')}</span>
                        </div>
                        <div className="doc-details">
                            <p><strong>{t('admin.email')}:</strong> {doc.email}</p>
                            <p><strong>{t('admin.phone')}:</strong> {doc.phone || 'N/A'}</p>
                            <p><strong>{t('admin.experience')}:</strong> {doc.experience || 'N/A'}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

// Appointments Overview
const AppointmentsOverview = () => {
    const { t } = useTranslation();
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const { getToken } = useAuth();

    useEffect(() => {
        const fetchAppointments = async () => {
            try {
                const response = await axios.get(`${API_URL}/admin/appointments`, { headers: { Authorization: `Bearer ${getToken()}` } });
                if (response.data.success) setAppointments(response.data.appointments);
            } catch (error) {
                toast.error('Failed to fetch appointments');
            } finally {
                setLoading(false);
            }
        };
        fetchAppointments();
    }, []);

    const getStatusBadge = (status) => {
        const classes = { pending: 'badge-warning', confirmed: 'badge-primary', completed: 'badge-success', cancelled: 'badge-error' };
        return <span className={`badge ${classes[status]}`}>{status}</span>;
    };

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="page-content animate-fadeIn">
            <div className="page-header">
                <h1><FaCalendarAlt /> {t('admin.allAppointments')}</h1>
                <p>{t('admin.systemRecords')}</p>
            </div>

            <div className="table-container card">
                <table className="data-table">
                    <thead><tr><th>{t('admin.date')}</th><th>{t('admin.time')}</th><th>{t('admin.predictedDisease')}</th><th>{t('admin.status')}</th></tr></thead>
                    <tbody>
                        {appointments.map(apt => (
                            <tr key={apt._id}>
                                <td>{apt.appointment_date}</td>
                                <td>{apt.appointment_time}</td>
                                <td>{apt.predicted_disease || 'N/A'}</td>
                                <td>{getStatusBadge(apt.status)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

// Medical Management - Unified Pharmacy with Medicine List
const MedicalManagement = () => {
    const { t } = useTranslation();
    const [medicals, setMedicals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [selectedMedical, setSelectedMedical] = useState(null);
    const [formData, setFormData] = useState({
        name: '', type: 'Medical Store', address: '', city: '', state: '', pincode: '',
        contact: '', hours: '', email: '', delivers: true
    });
    const [selectedMedicines, setSelectedMedicines] = useState([]);
    const { getToken } = useAuth();

    // Common CKD Medicines list
    const commonMedicines = [
        { name: 'Lisinopril (ACE Inhibitor)', category: 'Blood Pressure', purpose: 'Kidney protection & BP control' },
        { name: 'Losartan (ARB)', category: 'Blood Pressure', purpose: 'BP control, protects kidneys' },
        { name: 'Amlodipine', category: 'Blood Pressure', purpose: 'Calcium channel blocker for BP' },
        { name: 'Metformin', category: 'Diabetes', purpose: 'Blood sugar control (dose adjustment in CKD)' },
        { name: 'Dapagliflozin (SGLT2)', category: 'Diabetes/CKD', purpose: 'Blood sugar + kidney protection' },
        { name: 'Furosemide', category: 'Diuretic', purpose: 'Fluid retention management' },
        { name: 'Erythropoietin', category: 'Anemia', purpose: 'CKD-related anemia treatment' },
        { name: 'Iron Supplements', category: 'Anemia', purpose: 'Iron deficiency treatment' },
        { name: 'Calcium Acetate', category: 'Phosphate Binder', purpose: 'Controls phosphorus levels' },
        { name: 'Vitamin D (Calcitriol)', category: 'Supplements', purpose: 'Bone health in CKD' },
        { name: 'Sodium Bicarbonate', category: 'Acidosis', purpose: 'Treats metabolic acidosis' },
        { name: 'Atorvastatin', category: 'Cholesterol', purpose: 'Cardiovascular protection' }
    ];

    useEffect(() => { fetchMedicals(); }, []);

    const fetchMedicals = async () => {
        try {
            const res = await axios.get(`${API_URL}/pharmacy/admin/pharmacies`, { headers: { Authorization: `Bearer ${getToken()}` } });
            if (res.data.success) setMedicals(res.data.pharmacies);
        } catch (error) {
            console.error('Error fetching medicals');
        } finally {
            setLoading(false);
        }
    };

    const toggleMedicine = (idx) => {
        setSelectedMedicines(prev =>
            prev.includes(idx) ? prev.filter(i => i !== idx) : [...prev, idx]
        );
    };

    const selectAllMedicines = () => {
        if (selectedMedicines.length === commonMedicines.length) {
            setSelectedMedicines([]);
        } else {
            setSelectedMedicines(commonMedicines.map((_, idx) => idx));
        }
    };

    const handleAddMedical = async (e) => {
        e.preventDefault();
        try {
            const selectedMeds = selectedMedicines.map(idx => ({
                medicine_id: `med_${idx}`,
                name: commonMedicines[idx].name,
                category: commonMedicines[idx].category,
                purpose: commonMedicines[idx].purpose,
                in_stock: true,
                price: 0
            }));
            const dataWithMedicines = {
                ...formData,
                available_medicines: selectedMeds
            };
            const res = await axios.post(`${API_URL}/pharmacy/admin/pharmacy`, dataWithMedicines, { headers: { Authorization: `Bearer ${getToken()}` } });
            if (res.data.success) {
                toast.success(`Medical store added with ${selectedMeds.length} medicines!`);
                setShowForm(false);
                setFormData({ name: '', type: 'Medical Store', address: '', city: '', state: '', pincode: '', contact: '', hours: '', email: '', delivers: true });
                setSelectedMedicines([]);
                fetchMedicals();
            }
        } catch (error) {
            toast.error(error.response?.data?.message || 'Failed to add medical store');
        }
    };

    const handleDeleteMedical = async (id) => {
        if (!window.confirm('Delete this medical store?')) return;
        try {
            await axios.delete(`${API_URL}/pharmacy/admin/pharmacy/${id}`, { headers: { Authorization: `Bearer ${getToken()}` } });
            toast.success('Medical store deleted');
            setSelectedMedical(null);
            fetchMedicals();
        } catch (error) {
            toast.error('Failed to delete');
        }
    };

    const medicalTypes = ['Medical Store', 'Hospital Pharmacy', 'Chain Pharmacy', 'Online Pharmacy'];

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="page-content animate-fadeIn">
            <div className="page-header flex justify-between items-center">
                <div>
                    <h1><FaPills /> {t('admin.medicalStores')}</h1>
                    <p>{t('admin.manageMedicalStores')}</p>
                </div>
                <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
                    <FaPlus /> {t('admin.addMedicalStore')}
                </button>
            </div>

            {showForm && (
                <div className="card mb-6 animate-fadeIn">
                    <h3 className="mb-4">{t('admin.addMedicalStore')}</h3>
                    <form onSubmit={handleAddMedical}>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="form-group">
                                <label className="form-label">{t('admin.storeName')} *</label>
                                <input type="text" className="form-input" value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} required />
                            </div>
                            <div className="form-group">
                                <label className="form-label">{t('admin.type')} *</label>
                                <select className="form-select" value={formData.type} onChange={e => setFormData({ ...formData, type: e.target.value })}>
                                    {medicalTypes.map(t => <option key={t} value={t}>{t}</option>)}
                                </select>
                            </div>
                            <div className="form-group">
                                <label className="form-label">{t('admin.address')} *</label>
                                <input type="text" className="form-input" value={formData.address} onChange={e => setFormData({ ...formData, address: e.target.value })} required />
                            </div>
                            <div className="form-group">
                                <label className="form-label">{t('admin.city')} *</label>
                                <input type="text" className="form-input" value={formData.city} onChange={e => setFormData({ ...formData, city: e.target.value })} required />
                            </div>
                            <div className="form-group">
                                <label className="form-label">{t('admin.state')}</label>
                                <input type="text" className="form-input" value={formData.state} onChange={e => setFormData({ ...formData, state: e.target.value })} />
                            </div>
                            <div className="form-group">
                                <label className="form-label">{t('admin.pincode')}</label>
                                <input type="text" className="form-input" value={formData.pincode} onChange={e => setFormData({ ...formData, pincode: e.target.value })} />
                            </div>
                            <div className="form-group">
                                <label className="form-label">{t('admin.contact')} *</label>
                                <input type="text" className="form-input" value={formData.contact} onChange={e => setFormData({ ...formData, contact: e.target.value })} required />
                            </div>
                            <div className="form-group">
                                <label className="form-label">{t('admin.hours')} *</label>
                                <input type="text" className="form-input" placeholder="e.g., 8 AM - 10 PM" value={formData.hours} onChange={e => setFormData({ ...formData, hours: e.target.value })} required />
                            </div>
                        </div>

                        <div style={{ marginTop: '1rem', padding: '1rem', background: 'var(--gray-50)', borderRadius: '8px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                                <h4 style={{ margin: 0 }}>💊 {t('admin.selectCkdMedicines')} ({selectedMedicines.length} selected)</h4>
                                <button type="button" className="btn btn-sm" onClick={selectAllMedicines} style={{ padding: '0.25rem 0.75rem' }}>
                                    {selectedMedicines.length === commonMedicines.length ? t('admin.deselectAll') : t('admin.selectAll')}
                                </button>
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '0.5rem' }}>
                                {commonMedicines.map((med, idx) => (
                                    <label key={idx} style={{
                                        display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 0.75rem',
                                        background: selectedMedicines.includes(idx) ? 'var(--primary-50)' : 'white',
                                        border: selectedMedicines.includes(idx) ? '2px solid var(--primary-500)' : '1px solid var(--gray-200)',
                                        borderRadius: '6px', cursor: 'pointer', transition: 'all 0.2s'
                                    }}>
                                        <input
                                            type="checkbox"
                                            checked={selectedMedicines.includes(idx)}
                                            onChange={() => toggleMedicine(idx)}
                                            style={{ width: '18px', height: '18px', accentColor: 'var(--primary-500)' }}
                                        />
                                        <div style={{ flex: 1 }}>
                                            <div style={{ fontWeight: '500', fontSize: '0.85rem' }}>{med.name}</div>
                                            <div style={{ fontSize: '0.75rem', color: 'var(--gray-500)' }}>{med.category}</div>
                                        </div>
                                    </label>
                                ))}
                            </div>
                        </div>

                        <div className="flex gap-3 mt-4">
                            <button type="submit" className="btn btn-primary">{t('admin.addMedicalStore')}</button>
                            <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>{t('admin.cancel')}</button>
                        </div>
                    </form>
                </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1.5rem' }}>
                {medicals.map(medical => (
                    <div key={medical._id} className="card" style={{ cursor: 'pointer', transition: 'all 0.3s', border: selectedMedical?._id === medical._id ? '2px solid var(--primary-500)' : '1px solid var(--gray-200)' }} onClick={() => setSelectedMedical(selectedMedical?._id === medical._id ? null : medical)}>
                        <div className="flex justify-between items-start mb-3">
                            <div>
                                <h3 style={{ marginBottom: '0.25rem' }}>{medical.name}</h3>
                                <span className="badge badge-primary">{medical.type}</span>
                            </div>
                            <button className="btn btn-sm btn-danger" onClick={(e) => { e.stopPropagation(); handleDeleteMedical(medical._id); }}>
                                <FaTrash />
                            </button>
                        </div>

                        <div style={{ fontSize: '0.9rem', color: 'var(--gray-600)', marginBottom: '0.5rem' }}>
                            <p>📍 {medical.address}, {medical.city}{medical.state ? `, ${medical.state}` : ''}{medical.pincode ? ` - ${medical.pincode}` : ''}</p>
                            <p>📞 {medical.contact} | ⏰ {medical.hours}</p>
                        </div>

                        <div className="flex gap-2 mt-2">
                            <span className="badge badge-success">{t('admin.medicinesCount', { count: medical.total_medicines || medical.available_medicines?.length || 12 })}</span>
                            {medical.delivers && <span className="badge badge-warning">{t('admin.homeDelivery')}</span>}
                        </div>

                        {selectedMedical?._id === medical._id && (
                            <div style={{ marginTop: '1rem', padding: '1rem', background: 'var(--gray-50)', borderRadius: '8px' }}>
                                <h4 style={{ marginBottom: '0.75rem' }}>💊 {t('admin.availableMedicines')}</h4>
                                <div style={{ display: 'grid', gap: '0.5rem' }}>
                                    {(medical.available_medicines?.length > 0 ? medical.available_medicines : commonMedicines).map((med, idx) => (
                                        <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', background: 'white', borderRadius: '6px', fontSize: '0.85rem' }}>
                                            <span><strong>{med.name}</strong></span>
                                            <span style={{ color: 'var(--primary-500)' }}>{med.category}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {medicals.length === 0 && (
                <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
                    <FaPills style={{ fontSize: '3rem', color: 'var(--gray-300)', marginBottom: '1rem' }} />
                    <h3>{t('admin.noMedicalStores')}</h3>
                    <p style={{ color: 'var(--gray-500)' }}>{t('admin.addStoreDesc')}</p>
                </div>
            )}
        </div>
    );
};



// Main Admin Dashboard
const AdminDashboard = () => {
    const { t } = useTranslation();
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => { logout(); navigate('/'); };

    return (
        <div className="dashboard">
            <aside className="sidebar admin-sidebar">
                <div className="sidebar-header">
                    <FaHeartbeat className="sidebar-logo" />
                    <span>{t('landing.brand')}</span>
                </div>
                <nav className="sidebar-nav">
                    <Link to="/admin" className="nav-item"><FaChartBar /> {t('admin.dashboard')}</Link>
                    <Link to="/admin/users" className="nav-item"><FaUsers /> {t('admin.users')}</Link>
                    <Link to="/admin/doctors" className="nav-item"><FaUserMd /> {t('admin.doctors')}</Link>
                    <Link to="/admin/pharmacy" className="nav-item"><FaPills /> {t('patient.pharmacy')}</Link>
                    <Link to="/admin/appointments" className="nav-item"><FaCalendarAlt /> {t('admin.appointments')}</Link>
                </nav>
                <div className="sidebar-footer">
                    <div className="sidebar-language">
                        <LanguageSwitcher />
                    </div>
                    <div className="user-info">
                        <FaUserShield className="user-avatar" />
                        <div>
                            <span className="user-name">{user?.name}</span>
                            <span className="user-role">Admin</span>
                        </div>
                    </div>
                    <button onClick={handleLogout} className="logout-btn"><FaSignOutAlt /> {t('common.logout')}</button>
                </div>
            </aside>
            <main className="main-content">
                <Routes>
                    <Route path="/" element={<AdminOverview />} />
                    <Route path="/users" element={<UsersManagement />} />
                    <Route path="/doctors" element={<DoctorManagement />} />
                    <Route path="/pharmacy" element={<MedicalManagement />} />
                    <Route path="/appointments" element={<AppointmentsOverview />} />
                </Routes>
            </main>
        </div>
    );
};

export default AdminDashboard;

