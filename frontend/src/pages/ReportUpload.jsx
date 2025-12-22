import React, { useState, useRef } from 'react';
import { FaFileUpload, FaFilePdf, FaCheckCircle, FaExclamationTriangle, FaBrain, FaSpinner, FaDownload, FaInfoCircle } from 'react-icons/fa';
import { toast } from 'react-toastify';
import axios from 'axios';
import { saveAs } from 'file-saver';
import { useAuth, API_URL } from '../App';
import './CKDTestForm.css';

const ReportUpload = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [extractedData, setExtractedData] = useState(null);
    const [predicting, setPredicting] = useState(false);
    const [prediction, setPrediction] = useState(null);
    const [predictionId, setPredictionId] = useState(null);
    const [downloadingPdf, setDownloadingPdf] = useState(false);
    const fileInputRef = useRef(null);
    const { getToken } = useAuth();

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (file.type !== 'application/pdf') {
                toast.error('Please select a PDF file');
                return;
            }
            if (file.size > 10 * 1024 * 1024) { // 10MB limit
                toast.error('File size should be less than 10MB');
                return;
            }
            setSelectedFile(file);
            setExtractedData(null);
            setPrediction(null);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        const file = e.dataTransfer.files[0];
        if (file && file.type === 'application/pdf') {
            setSelectedFile(file);
            setExtractedData(null);
            setPrediction(null);
        } else {
            toast.error('Please drop a PDF file');
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
    };

    const uploadAndExtract = async () => {
        if (!selectedFile) {
            toast.error('Please select a file first');
            return;
        }

        setUploading(true);
        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await axios.post(`${API_URL}/report/upload`, formData, {
                headers: {
                    'Authorization': `Bearer ${getToken()}`,
                    'Content-Type': 'multipart/form-data'
                }
            });

            if (response.data.success) {
                setExtractedData(response.data);
                toast.success(`Extracted ${response.data.parameters_found} parameters from report!`);
            } else {
                toast.error(response.data.message);
            }
        } catch (error) {
            toast.error(error.response?.data?.message || 'Failed to process report');
        } finally {
            setUploading(false);
        }
    };

    const makePrediction = async () => {
        if (!extractedData?.prediction_data) {
            toast.error('No extracted data available');
            return;
        }

        setPredicting(true);
        try {
            const response = await axios.post(`${API_URL}/hybrid/predict`,
                extractedData.prediction_data,
                { headers: { Authorization: `Bearer ${getToken()}` } }
            );

            if (response.data.success) {
                setPrediction(response.data.prediction);
                setPredictionId(response.data.prediction_id);
                toast.success('CKD prediction complete!');
            }
        } catch (error) {
            toast.error('Prediction failed');
        } finally {
            setPredicting(false);
        }
    };

    const handleDownloadPdf = async () => {
        if (!predictionId && !prediction) {
            toast.error('No prediction available');
            return;
        }

        setDownloadingPdf(true);
        try {
            const response = await axios.post(`${API_URL}/xai/report/generate`,
                {
                    prediction: prediction,
                    input_data: extractedData?.prediction_data,
                    model_details: {},
                    xai_explanation: {}
                },
                {
                    headers: { Authorization: `Bearer ${getToken()}` },
                    responseType: 'blob'
                }
            );

            const blob = new Blob([response.data], { type: 'application/pdf' });
            saveAs(blob, `CKD_Report_${new Date().toISOString().slice(0, 10)}.pdf`);
            toast.success('PDF downloaded!');
        } catch (error) {
            toast.error('Failed to download PDF');
        } finally {
            setDownloadingPdf(false);
        }
    };

    const resetUpload = () => {
        setSelectedFile(null);
        setExtractedData(null);
        setPrediction(null);
        setPredictionId(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    return (
        <div className="gemini-container">
            <div className="gemini-header">
                <div className="gemini-title">
                    <FaFileUpload className="title-icon" />
                    <div>
                        <h1>Upload Health Report</h1>
                        <p>Upload your medical report (PDF) for automatic CKD analysis</p>
                    </div>
                </div>
            </div>

            {/* Upload Section */}
            {!extractedData && !prediction && (
                <div className="gemini-form-container">
                    <div
                        className="upload-zone"
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                        onClick={() => fileInputRef.current?.click()}
                        style={{
                            border: '3px dashed var(--primary-300)',
                            borderRadius: '16px',
                            padding: '3rem',
                            textAlign: 'center',
                            cursor: 'pointer',
                            background: selectedFile ? 'var(--success-50)' : 'var(--gray-50)',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleFileSelect}
                            accept=".pdf"
                            style={{ display: 'none' }}
                        />

                        {selectedFile ? (
                            <div>
                                <FaFilePdf style={{ fontSize: '4rem', color: 'var(--error-500)', marginBottom: '1rem' }} />
                                <h3 style={{ marginBottom: '0.5rem' }}>{selectedFile.name}</h3>
                                <p style={{ color: 'var(--gray-500)' }}>
                                    Size: {(selectedFile.size / 1024).toFixed(1)} KB
                                </p>
                            </div>
                        ) : (
                            <div>
                                <FaFileUpload style={{ fontSize: '4rem', color: 'var(--primary-400)', marginBottom: '1rem' }} />
                                <h3 style={{ marginBottom: '0.5rem' }}>Drop your medical report here</h3>
                                <p style={{ color: 'var(--gray-500)' }}>or click to browse (PDF only, max 10MB)</p>
                            </div>
                        )}
                    </div>

                    {/* Supported Parameters Info */}
                    <div className="card" style={{ marginTop: '2rem', padding: '1.5rem' }}>
                        <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <FaInfoCircle style={{ color: 'var(--primary-500)' }} />
                            Supported Medical Parameters
                        </h3>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.5rem' }}>
                            {[
                                'Specific Gravity (sg)', 'Albumin (al)', 'Sugar (su)',
                                'Blood Glucose Random', 'Blood Urea', 'Serum Creatinine',
                                'Hemoglobin', 'Packed Cell Volume', 'WBC Count', 'RBC Count',
                                'Hypertension', 'Diabetes Mellitus', 'Coronary Artery Disease',
                                'Appetite', 'Pedal Edema', 'Anemia'
                            ].map((param, idx) => (
                                <span key={idx} style={{
                                    padding: '0.5rem 0.75rem',
                                    background: 'var(--gray-100)',
                                    borderRadius: '8px',
                                    fontSize: '0.875rem'
                                }}>
                                    ✓ {param}
                                </span>
                            ))}
                        </div>
                    </div>

                    {selectedFile && (
                        <div style={{ marginTop: '1.5rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                            <button
                                className="gemini-btn secondary"
                                onClick={resetUpload}
                            >
                                Cancel
                            </button>
                            <button
                                className="gemini-btn primary"
                                onClick={uploadAndExtract}
                                disabled={uploading}
                            >
                                {uploading ? (
                                    <><FaSpinner className="spin" /> Processing...</>
                                ) : (
                                    <><FaBrain /> Extract & Analyze</>
                                )}
                            </button>
                        </div>
                    )}
                </div>
            )}

            {/* Extracted Data Section */}
            {extractedData && !prediction && (
                <div className="gemini-form-container">
                    <div className="card" style={{ padding: '2rem', background: 'linear-gradient(135deg, var(--success-50), white)' }}>
                        <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <FaCheckCircle style={{ color: 'var(--success-500)' }} />
                            Parameters Extracted Successfully
                        </h2>

                        <p style={{ marginBottom: '1rem', color: 'var(--gray-600)' }}>
                            Found <strong>{extractedData.parameters_found}</strong> medical parameters in your report
                        </p>

                        {/* Extracted Values Table */}
                        <div style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                            gap: '1rem',
                            marginBottom: '2rem'
                        }}>
                            {Object.entries(extractedData.extracted_values).map(([key, value]) => (
                                <div key={key} style={{
                                    padding: '1rem',
                                    background: 'white',
                                    borderRadius: '12px',
                                    boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                                    border: '1px solid var(--gray-200)'
                                }}>
                                    <span style={{
                                        display: 'block',
                                        fontSize: '0.75rem',
                                        color: 'var(--gray-500)',
                                        textTransform: 'uppercase',
                                        marginBottom: '0.25rem'
                                    }}>
                                        {key}
                                    </span>
                                    <span style={{
                                        fontSize: '1.25rem',
                                        fontWeight: '700',
                                        color: 'var(--gray-900)'
                                    }}>
                                        {value}
                                    </span>
                                </div>
                            ))}
                        </div>

                        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                            <button className="gemini-btn secondary" onClick={resetUpload}>
                                Upload Different Report
                            </button>
                            <button
                                className="gemini-btn primary analyze"
                                onClick={makePrediction}
                                disabled={predicting}
                            >
                                {predicting ? (
                                    <><FaSpinner className="spin" /> Predicting...</>
                                ) : (
                                    <><FaBrain /> Predict CKD</>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Prediction Results */}
            {prediction && (
                <div className="gemini-results">
                    <div className="gemini-results-content">
                        <div className={`gemini-result-card ${prediction.result === 'ckd' ? 'risk-high' : 'risk-low'}`}>
                            <div className="result-header">
                                {prediction.result === 'ckd' ? (
                                    <FaExclamationTriangle className="result-icon warning" />
                                ) : (
                                    <FaCheckCircle className="result-icon success" />
                                )}
                                <div>
                                    <h2>{prediction.result === 'ckd' ? 'CKD Indicators Detected' : 'No CKD Indicators'}</h2>
                                    <p className="result-subtitle">Analysis from uploaded report</p>
                                </div>
                            </div>

                            <div className="result-metrics">
                                <div className="metric">
                                    <span className="metric-value">{prediction.confidence?.toFixed(1)}%</span>
                                    <span className="metric-label">Confidence</span>
                                </div>
                                <div className="metric">
                                    <span className={`metric-value risk-${prediction.risk_level?.toLowerCase()}`}>
                                        {prediction.risk_level}
                                    </span>
                                    <span className="metric-label">Risk Level</span>
                                </div>
                            </div>

                            <div className="result-actions">
                                <button
                                    className="gemini-btn primary download-btn"
                                    onClick={handleDownloadPdf}
                                    disabled={downloadingPdf}
                                >
                                    <FaDownload /> {downloadingPdf ? 'Generating...' : 'Download PDF Report'}
                                </button>
                            </div>

                            <div className="result-disclaimer">
                                <FaInfoCircle />
                                <span>This is a screening tool. Please consult a nephrologist for proper diagnosis.</span>
                            </div>
                        </div>

                        {/* Source Data Summary */}
                        <div className="card" style={{ marginTop: '1.5rem', padding: '1.5rem' }}>
                            <h3 style={{ marginBottom: '1rem' }}>📋 Report Summary</h3>
                            <p><strong>Source:</strong> {selectedFile?.name}</p>
                            <p><strong>Parameters Used:</strong> {extractedData?.parameters_found}</p>
                        </div>

                        <div className="quick-actions" style={{ marginTop: '1.5rem' }}>
                            <button className="gemini-btn secondary" onClick={resetUpload}>
                                Upload New Report
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ReportUpload;
