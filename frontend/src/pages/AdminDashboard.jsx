import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { FaHeartbeat, FaUsers, FaUserMd, FaCalendarAlt, FaChartBar, FaSignOutAlt, FaUserShield, FaPlus, FaTrash, FaSpinner, FaPills } from 'react-icons/fa';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useAuth, API_URL } from '../App';
import './Dashboard.css';

// Stats Overview
const AdminOverview = () => {
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
                <h1><FaChartBar /> Admin Dashboard</h1>
                <p>System overview and management</p>
            </div>

            <div className="stats-grid">
                <div className="card stat-card">
                    <div className="stat-icon blue"><FaUsers /></div>
                    <div className="stat-info"><h3>{stats.patients}</h3><p>Patients</p></div>
                </div>
                <div className="card stat-card">
                    <div className="stat-icon green"><FaUserMd /></div>
                    <div className="stat-info"><h3>{stats.doctors}</h3><p>Doctors</p></div>
                </div>
                <div className="card stat-card">
                    <div className="stat-icon orange"><FaCalendarAlt /></div>
                    <div className="stat-info"><h3>{stats.appointments}</h3><p>Appointments</p></div>
                </div>
                <div className="card stat-card">
                    <div className="stat-icon purple"><FaChartBar /></div>
                    <div className="stat-info"><h3>{stats.predictions}</h3><p>AI Predictions</p></div>
                </div>
            </div>

            <div className="grid grid-cols-2 mt-6">
                <div className="card">
                    <h3>Quick Actions</h3>
                    <div className="flex flex-col gap-3 mt-4">
                        <Link to="/admin/doctors" className="btn btn-primary">Manage Doctors</Link>
                        <Link to="/admin/users" className="btn btn-secondary">View All Users</Link>
                        <Link to="/admin/appointments" className="btn btn-secondary">View Appointments</Link>
                    </div>
                </div>
                <div className="card">
                    <h3>System Info</h3>
                    <div className="mt-4">
                        <p><strong>Database:</strong> MongoDB (missing_person)</p>
                        <p><strong>ML Model:</strong> Multinomial Naive Bayes</p>
                        <p><strong>Status:</strong> <span className="badge badge-success">Active</span></p>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Users Management
const UsersManagement = () => {
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
                <h1><FaUsers /> Users Management</h1>
                <p>View and manage all users</p>
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
                        <tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Actions</th></tr>
                    </thead>
                    <tbody>
                        {users.map(user => (
                            <tr key={user._id}>
                                <td><strong>{user.name}</strong></td>
                                <td>{user.email}</td>
                                <td><span className={`badge badge-${user.role === 'admin' ? 'error' : user.role === 'doctor' ? 'success' : 'primary'}`}>{user.role}</span></td>
                                <td><span className={`badge ${user.is_active !== false ? 'badge-success' : 'badge-error'}`}>{user.is_active !== false ? 'Active' : 'Inactive'}</span></td>
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
                <div><h1><FaUserMd /> Doctor Management</h1><p>Add and manage doctors</p></div>
                <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}><FaPlus /> Add Doctor</button>
            </div>

            {showForm && (
                <div className="card mb-6 animate-fadeIn">
                    <h3 className="mb-4">Add New Doctor</h3>
                    <form onSubmit={handleSubmit}>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="form-group">
                                <label className="form-label">Name *</label>
                                <input type="text" className="form-input" value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} required />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Email *</label>
                                <input type="email" className="form-input" value={formData.email} onChange={e => setFormData({ ...formData, email: e.target.value })} required />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Password *</label>
                                <input type="password" className="form-input" value={formData.password} onChange={e => setFormData({ ...formData, password: e.target.value })} required />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Specialization *</label>
                                <select className="form-select" value={formData.specialization} onChange={e => setFormData({ ...formData, specialization: e.target.value })} required>
                                    <option value="">Select</option>
                                    {specializations.map(s => <option key={s} value={s}>{s}</option>)}
                                </select>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Phone</label>
                                <input type="tel" className="form-input" value={formData.phone} onChange={e => setFormData({ ...formData, phone: e.target.value })} />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Experience</label>
                                <input type="text" className="form-input" placeholder="e.g., 5 years" value={formData.experience} onChange={e => setFormData({ ...formData, experience: e.target.value })} />
                            </div>
                        </div>
                        <div className="flex gap-3 mt-4">
                            <button type="submit" className="btn btn-primary">Add Doctor</button>
                            <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
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
                            <span className={`badge ${doc.is_active !== false ? 'badge-success' : 'badge-error'}`}>{doc.is_active !== false ? 'Active' : 'Inactive'}</span>
                        </div>
                        <div className="doc-details">
                            <p><strong>Email:</strong> {doc.email}</p>
                            <p><strong>Phone:</strong> {doc.phone || 'N/A'}</p>
                            <p><strong>Experience:</strong> {doc.experience || 'N/A'}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

// Appointments Overview
const AppointmentsOverview = () => {
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
                <h1><FaCalendarAlt /> All Appointments</h1>
                <p>System-wide appointment records</p>
            </div>

            <div className="table-container card">
                <table className="data-table">
                    <thead><tr><th>Date</th><th>Time</th><th>Predicted Disease</th><th>Status</th></tr></thead>
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

// Pharmacy Management
const PharmacyManagement = () => {
    const [pharmacies, setPharmacies] = useState([]);
    const [medicines, setMedicines] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showPharmacyForm, setShowPharmacyForm] = useState(false);
    const [showMedicineForm, setShowMedicineForm] = useState(false);
    const [activeTab, setActiveTab] = useState('pharmacies');
    const [pharmacyForm, setPharmacyForm] = useState({
        name: '', type: 'Chain Store', address: '', city: '', contact: '', hours: '', email: '', delivers: true
    });
    const [medicineForm, setMedicineForm] = useState({
        name: '', category: 'blood_pressure', purpose: '', notes: '', common_dosage: '', price_range: '', requires_prescription: true, ckd_relevance: 'Medium'
    });
    const { getToken } = useAuth();

    useEffect(() => { fetchData(); }, [activeTab]);

    const fetchData = async () => {
        try {
            if (activeTab === 'pharmacies') {
                const res = await axios.get(`${API_URL}/pharmacy/admin/pharmacies`, { headers: { Authorization: `Bearer ${getToken()}` } });
                if (res.data.success) setPharmacies(res.data.pharmacies);
            } else {
                const res = await axios.get(`${API_URL}/pharmacy/admin/medicines`, { headers: { Authorization: `Bearer ${getToken()}` } });
                if (res.data.success) setMedicines(res.data.medicines);
            }
        } catch (error) {
            toast.error('Failed to fetch data');
        } finally {
            setLoading(false);
        }
    };

    const handleAddPharmacy = async (e) => {
        e.preventDefault();
        try {
            const res = await axios.post(`${API_URL}/pharmacy/admin/pharmacy`, pharmacyForm, { headers: { Authorization: `Bearer ${getToken()}` } });
            if (res.data.success) {
                toast.success('Pharmacy added successfully');
                setShowPharmacyForm(false);
                setPharmacyForm({ name: '', type: 'Chain Store', address: '', city: '', contact: '', hours: '', email: '', delivers: true });
                fetchData();
            }
        } catch (error) {
            toast.error(error.response?.data?.message || 'Failed to add pharmacy');
        }
    };

    const handleAddMedicine = async (e) => {
        e.preventDefault();
        try {
            const res = await axios.post(`${API_URL}/pharmacy/admin/medicine`, medicineForm, { headers: { Authorization: `Bearer ${getToken()}` } });
            if (res.data.success) {
                toast.success('Medicine added successfully');
                setShowMedicineForm(false);
                setMedicineForm({ name: '', category: 'blood_pressure', purpose: '', notes: '', common_dosage: '', price_range: '', requires_prescription: true, ckd_relevance: 'Medium' });
                fetchData();
            }
        } catch (error) {
            toast.error(error.response?.data?.message || 'Failed to add medicine');
        }
    };

    const handleDeletePharmacy = async (id) => {
        if (!window.confirm('Delete this pharmacy?')) return;
        try {
            await axios.delete(`${API_URL}/pharmacy/admin/pharmacy/${id}`, { headers: { Authorization: `Bearer ${getToken()}` } });
            toast.success('Pharmacy deleted');
            fetchData();
        } catch (error) {
            toast.error('Failed to delete');
        }
    };

    const handleDeleteMedicine = async (id) => {
        if (!window.confirm('Delete this medicine?')) return;
        try {
            await axios.delete(`${API_URL}/pharmacy/admin/medicine/${id}`, { headers: { Authorization: `Bearer ${getToken()}` } });
            toast.success('Medicine deleted');
            fetchData();
        } catch (error) {
            toast.error('Failed to delete');
        }
    };

    const pharmacyTypes = ['Chain Store', 'Hospital Pharmacy', 'Retail Pharmacy', 'Online Pharmacy'];
    const categories = [
        { id: 'blood_pressure', name: 'Antihypertensives' },
        { id: 'diabetes_management', name: 'Antidiabetics' },
        { id: 'anemia_management', name: 'Anemia Treatment' },
        { id: 'phosphate_binders', name: 'Mineral Management' },
        { id: 'supplements', name: 'Nutritional Supplements' },
        { id: 'potassium_management', name: 'Electrolyte Management' }
    ];

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="page-content animate-fadeIn">
            <div className="page-header flex justify-between items-center">
                <div><h1><FaPills /> Pharmacy & Medicines</h1><p>Manage pharmacies and CKD medications</p></div>
                <div className="flex gap-3">
                    {activeTab === 'pharmacies' ? (
                        <button className="btn btn-primary" onClick={() => setShowPharmacyForm(!showPharmacyForm)}><FaPlus /> Add Pharmacy</button>
                    ) : (
                        <button className="btn btn-primary" onClick={() => setShowMedicineForm(!showMedicineForm)}><FaPlus /> Add Medicine</button>
                    )}
                </div>
            </div>

            <div className="filter-tabs mb-4">
                <button className={`filter-tab ${activeTab === 'pharmacies' ? 'active' : ''}`} onClick={() => setActiveTab('pharmacies')}>
                    Pharmacies ({pharmacies.length})
                </button>
                <button className={`filter-tab ${activeTab === 'medicines' ? 'active' : ''}`} onClick={() => setActiveTab('medicines')}>
                    Medicines ({medicines.length})
                </button>
            </div>

            {showPharmacyForm && (
                <div className="card mb-6 animate-fadeIn">
                    <h3 className="mb-4">Add New Pharmacy</h3>
                    <form onSubmit={handleAddPharmacy}>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="form-group">
                                <label className="form-label">Name *</label>
                                <input type="text" className="form-input" value={pharmacyForm.name} onChange={e => setPharmacyForm({ ...pharmacyForm, name: e.target.value })} required />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Type *</label>
                                <select className="form-select" value={pharmacyForm.type} onChange={e => setPharmacyForm({ ...pharmacyForm, type: e.target.value })}>
                                    {pharmacyTypes.map(t => <option key={t} value={t}>{t}</option>)}
                                </select>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Address *</label>
                                <input type="text" className="form-input" value={pharmacyForm.address} onChange={e => setPharmacyForm({ ...pharmacyForm, address: e.target.value })} required />
                            </div>
                            <div className="form-group">
                                <label className="form-label">City</label>
                                <input type="text" className="form-input" value={pharmacyForm.city} onChange={e => setPharmacyForm({ ...pharmacyForm, city: e.target.value })} />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Contact *</label>
                                <input type="text" className="form-input" value={pharmacyForm.contact} onChange={e => setPharmacyForm({ ...pharmacyForm, contact: e.target.value })} required />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Hours *</label>
                                <input type="text" className="form-input" placeholder="e.g., 8 AM - 10 PM" value={pharmacyForm.hours} onChange={e => setPharmacyForm({ ...pharmacyForm, hours: e.target.value })} required />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Email</label>
                                <input type="email" className="form-input" value={pharmacyForm.email} onChange={e => setPharmacyForm({ ...pharmacyForm, email: e.target.value })} />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Delivery Available</label>
                                <select className="form-select" value={pharmacyForm.delivers} onChange={e => setPharmacyForm({ ...pharmacyForm, delivers: e.target.value === 'true' })}>
                                    <option value="true">Yes</option>
                                    <option value="false">No</option>
                                </select>
                            </div>
                        </div>
                        <div className="flex gap-3 mt-4">
                            <button type="submit" className="btn btn-primary">Add Pharmacy</button>
                            <button type="button" className="btn btn-secondary" onClick={() => setShowPharmacyForm(false)}>Cancel</button>
                        </div>
                    </form>
                </div>
            )}

            {showMedicineForm && (
                <div className="card mb-6 animate-fadeIn">
                    <h3 className="mb-4">Add New Medicine</h3>
                    <form onSubmit={handleAddMedicine}>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="form-group">
                                <label className="form-label">Name *</label>
                                <input type="text" className="form-input" value={medicineForm.name} onChange={e => setMedicineForm({ ...medicineForm, name: e.target.value })} required />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Category *</label>
                                <select className="form-select" value={medicineForm.category} onChange={e => setMedicineForm({ ...medicineForm, category: e.target.value })}>
                                    {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                </select>
                            </div>
                            <div className="form-group col-span-2">
                                <label className="form-label">Purpose *</label>
                                <input type="text" className="form-input" value={medicineForm.purpose} onChange={e => setMedicineForm({ ...medicineForm, purpose: e.target.value })} required />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Dosage</label>
                                <input type="text" className="form-input" value={medicineForm.common_dosage} onChange={e => setMedicineForm({ ...medicineForm, common_dosage: e.target.value })} />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Price Range</label>
                                <input type="text" className="form-input" placeholder="e.g., ₹50-200" value={medicineForm.price_range} onChange={e => setMedicineForm({ ...medicineForm, price_range: e.target.value })} />
                            </div>
                            <div className="form-group">
                                <label className="form-label">CKD Relevance</label>
                                <select className="form-select" value={medicineForm.ckd_relevance} onChange={e => setMedicineForm({ ...medicineForm, ckd_relevance: e.target.value })}>
                                    <option value="High">High</option>
                                    <option value="Medium">Medium</option>
                                    <option value="Low">Low</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Prescription Required</label>
                                <select className="form-select" value={medicineForm.requires_prescription} onChange={e => setMedicineForm({ ...medicineForm, requires_prescription: e.target.value === 'true' })}>
                                    <option value="true">Yes</option>
                                    <option value="false">No</option>
                                </select>
                            </div>
                            <div className="form-group col-span-2">
                                <label className="form-label">Notes</label>
                                <textarea className="form-input" rows="2" value={medicineForm.notes} onChange={e => setMedicineForm({ ...medicineForm, notes: e.target.value })}></textarea>
                            </div>
                        </div>
                        <div className="flex gap-3 mt-4">
                            <button type="submit" className="btn btn-primary">Add Medicine</button>
                            <button type="button" className="btn btn-secondary" onClick={() => setShowMedicineForm(false)}>Cancel</button>
                        </div>
                    </form>
                </div>
            )}

            {activeTab === 'pharmacies' ? (
                <div className="table-container card">
                    <table className="data-table">
                        <thead>
                            <tr><th>Name</th><th>Type</th><th>Address</th><th>Contact</th><th>Hours</th><th>Delivery</th><th>Actions</th></tr>
                        </thead>
                        <tbody>
                            {pharmacies.map(p => (
                                <tr key={p._id}>
                                    <td><strong>{p.name}</strong></td>
                                    <td><span className="badge badge-primary">{p.type}</span></td>
                                    <td>{p.address}, {p.city}</td>
                                    <td>{p.contact}</td>
                                    <td>{p.hours}</td>
                                    <td>{p.delivers ? <span className="badge badge-success">Yes</span> : <span className="badge badge-error">No</span>}</td>
                                    <td>
                                        <button className="btn btn-sm btn-danger" onClick={() => handleDeletePharmacy(p._id)}><FaTrash /></button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ) : (
                <div className="table-container card">
                    <table className="data-table">
                        <thead>
                            <tr><th>Name</th><th>Category</th><th>Purpose</th><th>Dosage</th><th>Rx</th><th>CKD Relevance</th><th>Actions</th></tr>
                        </thead>
                        <tbody>
                            {medicines.map(m => (
                                <tr key={m._id}>
                                    <td><strong>{m.name}</strong></td>
                                    <td><span className="badge badge-primary">{m.category_name}</span></td>
                                    <td>{m.purpose}</td>
                                    <td>{m.common_dosage}</td>
                                    <td>{m.requires_prescription ? <span className="badge badge-warning">Rx</span> : <span className="badge badge-success">OTC</span>}</td>
                                    <td><span className={`badge ${m.ckd_relevance === 'High' ? 'badge-error' : m.ckd_relevance === 'Medium' ? 'badge-warning' : 'badge-success'}`}>{m.ckd_relevance}</span></td>
                                    <td>
                                        <button className="btn btn-sm btn-danger" onClick={() => handleDeleteMedicine(m._id)}><FaTrash /></button>
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

// Main Admin Dashboard
const AdminDashboard = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => { logout(); navigate('/'); };

    return (
        <div className="dashboard">
            <aside className="sidebar admin-sidebar">
                <div className="sidebar-header">
                    <FaHeartbeat className="sidebar-logo" />
                    <span>CKD Predictor</span>
                </div>
                <nav className="sidebar-nav">
                    <Link to="/admin" className="nav-item"><FaChartBar /> Dashboard</Link>
                    <Link to="/admin/users" className="nav-item"><FaUsers /> Users</Link>
                    <Link to="/admin/doctors" className="nav-item"><FaUserMd /> Doctors</Link>
                    <Link to="/admin/pharmacy" className="nav-item"><FaPills /> Pharmacy</Link>
                    <Link to="/admin/appointments" className="nav-item"><FaCalendarAlt /> Appointments</Link>
                </nav>
                <div className="sidebar-footer">
                    <div className="user-info">
                        <FaUserShield className="user-avatar" />
                        <div>
                            <span className="user-name">{user?.name}</span>
                            <span className="user-role">Admin</span>
                        </div>
                    </div>
                    <button onClick={handleLogout} className="logout-btn"><FaSignOutAlt /> Logout</button>
                </div>
            </aside>
            <main className="main-content">
                <Routes>
                    <Route path="/" element={<AdminOverview />} />
                    <Route path="/users" element={<UsersManagement />} />
                    <Route path="/doctors" element={<DoctorManagement />} />
                    <Route path="/pharmacy" element={<PharmacyManagement />} />
                    <Route path="/appointments" element={<AppointmentsOverview />} />
                </Routes>
            </main>
        </div>
    );
};

export default AdminDashboard;

