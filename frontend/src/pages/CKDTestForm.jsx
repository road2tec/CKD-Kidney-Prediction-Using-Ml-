import React, { useState } from 'react';
import { FaFlask, FaBrain, FaAppleAlt, FaChevronRight, FaChevronLeft, FaCheckCircle, FaExclamationTriangle, FaInfoCircle, FaDownload, FaBalanceScale, FaPills, FaVideo } from 'react-icons/fa';
import { toast } from 'react-toastify';
import axios from 'axios';
import { saveAs } from 'file-saver';
import { useAuth, API_URL } from '../App';
import './CKDTestForm.css';

const CKDTestForm = () => {
    const [currentStep, setCurrentStep] = useState(0);
    const [formData, setFormData] = useState({
        age: '',
        bp: '',
        sg: '1.020',
        al: '0',
        su: '0',
        bgr: '',
        bu: '',
        sc: '',
        sod: '',
        pot: '',
        hemo: '',
        pcv: '',
        wc: '',
        rc: '',
        rbc: 'normal',
        pc: 'normal',
        pcc: 'notpresent',
        ba: 'notpresent',
        htn: 'no',
        dm: 'no',
        cad: 'no',
        appet: 'good',
        pe: 'no',
        ane: 'no'
    });

    const [loading, setLoading] = useState(false);
    const [prediction, setPrediction] = useState(null);
    const [modelDetails, setModelDetails] = useState(null);
    const [explanation, setExplanation] = useState(null);
    const [recommendations, setRecommendations] = useState(null);
    const [predictionId, setPredictionId] = useState(null);
    const [downloadingPdf, setDownloadingPdf] = useState(false);
    const { getToken } = useAuth();

    const steps = [
        { title: 'Basic Info', icon: '👤', description: 'Age & Blood Pressure' },
        { title: 'Urine Tests', icon: '🧪', description: 'Urine Analysis Results' },
        { title: 'Blood Tests', icon: '💉', description: 'Blood Work Results' },
        { title: 'Medical History', icon: '📋', description: 'Health Conditions' },
        { title: 'Results', icon: '📊', description: 'Hybrid AI Analysis' }
    ];

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const nextStep = () => {
        if (currentStep < steps.length - 1) {
            setCurrentStep(prev => prev + 1);
        }
    };

    const prevStep = () => {
        if (currentStep > 0) {
            setCurrentStep(prev => prev - 1);
        }
    };

    const handleAnalyze = async () => {
        setLoading(true);
        setPrediction(null);
        setExplanation(null);
        setRecommendations(null);
        setModelDetails(null);
        setCurrentStep(4);

        try {
            // Use Hybrid AI endpoint
            const predResponse = await axios.post(`${API_URL}/hybrid/predict`,
                formData,
                { headers: { Authorization: `Bearer ${getToken()}` } }
            );

            if (predResponse.data.success) {
                setPrediction(predResponse.data.prediction);
                setExplanation(predResponse.data.xai_explanation);
                setModelDetails(predResponse.data.model_details);
                setPredictionId(predResponse.data.prediction_id);
                toast.success('Hybrid AI analysis complete!');

                // Get recommendations
                try {
                    const recResponse = await axios.post(`${API_URL}/recommendations/lifestyle`,
                        {
                            prediction: predResponse.data.prediction.result,
                            risk_level: predResponse.data.prediction.risk_level,
                            age: formData.age,
                            weight: 70,
                            htn: formData.htn,
                            dm: formData.dm
                        },
                        { headers: { Authorization: `Bearer ${getToken()}` } }
                    );
                    if (recResponse.data.success) {
                        setRecommendations(recResponse.data.recommendations);
                    }
                } catch (err) {
                    console.log('Recommendations not available');
                }
            }
        } catch (error) {
            toast.error(error.response?.data?.message || 'Analysis failed');
            setCurrentStep(3);
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadPdf = async () => {
        if (!predictionId && !prediction) {
            toast.error('No prediction available for download');
            return;
        }

        setDownloadingPdf(true);
        try {
            let response;

            // Try fetching by prediction ID first
            if (predictionId) {
                try {
                    response = await axios.get(`${API_URL}/xai/report/pdf/${predictionId}`, {
                        headers: { Authorization: `Bearer ${getToken()}` },
                        responseType: 'blob'
                    });
                } catch (idError) {
                    console.log('ID-based download failed, trying generate endpoint');
                    // Fall back to generate endpoint
                    response = await axios.post(`${API_URL}/xai/report/generate`,
                        {
                            prediction: prediction,
                            input_data: formData,
                            model_details: modelDetails,
                            xai_explanation: explanation
                        },
                        {
                            headers: { Authorization: `Bearer ${getToken()}` },
                            responseType: 'blob'
                        }
                    );
                }
            } else {
                // Use generate endpoint directly
                response = await axios.post(`${API_URL}/xai/report/generate`,
                    {
                        prediction: prediction,
                        input_data: formData,
                        model_details: modelDetails,
                        xai_explanation: explanation
                    },
                    {
                        headers: { Authorization: `Bearer ${getToken()}` },
                        responseType: 'blob'
                    }
                );
            }

            // Check if response is actually a PDF
            const contentType = response.headers['content-type'];
            if (contentType && contentType.includes('application/json')) {
                // API returned an error as JSON
                const text = await response.data.text();
                const errorData = JSON.parse(text);
                toast.error(errorData.message || 'Failed to generate PDF');
                return;
            }

            // Create blob and use file-saver for reliable download
            const blob = new Blob([response.data], { type: 'application/pdf' });
            const filename = predictionId
                ? `CKD_Report_${predictionId.substring(0, 8)}.pdf`
                : `CKD_Report_${new Date().toISOString().slice(0, 10)}.pdf`;

            // Use file-saver for proper filename
            saveAs(blob, filename);

            toast.success('PDF report downloaded successfully!');
        } catch (error) {
            console.error('PDF download error:', error);
            toast.error(error.response?.data?.message || 'Failed to download PDF report');
        } finally {
            setDownloadingPdf(false);
        }
    };


    const resetForm = () => {
        setCurrentStep(0);
        setPrediction(null);
        setExplanation(null);
        setRecommendations(null);
        setModelDetails(null);
        setPredictionId(null);
    };

    const renderStepContent = () => {
        switch (currentStep) {
            case 0:
                return (
                    <div className="gemini-step-content">
                        <div className="gemini-input-group">
                            <label>Age (years)</label>
                            <input
                                type="number"
                                name="age"
                                value={formData.age}
                                onChange={handleInputChange}
                                placeholder="Enter your age"
                                className="gemini-input"
                            />
                            <span className="input-hint">Normal range: 18-100</span>
                        </div>
                        <div className="gemini-input-group">
                            <label>Blood Pressure (mm/Hg)</label>
                            <input
                                type="number"
                                name="bp"
                                value={formData.bp}
                                onChange={handleInputChange}
                                placeholder="Diastolic BP (e.g., 80)"
                                className="gemini-input"
                            />
                            <span className="input-hint">Normal: 60-80 mm/Hg</span>
                        </div>
                    </div>
                );

            case 1:
                return (
                    <div className="gemini-step-content">
                        <div className="gemini-input-row">
                            <div className="gemini-input-group">
                                <label>Specific Gravity</label>
                                <select name="sg" value={formData.sg} onChange={handleInputChange} className="gemini-select">
                                    <option value="1.005">1.005</option>
                                    <option value="1.010">1.010</option>
                                    <option value="1.015">1.015</option>
                                    <option value="1.020">1.020</option>
                                    <option value="1.025">1.025</option>
                                </select>
                            </div>
                            <div className="gemini-input-group">
                                <label>Albumin (0-5)</label>
                                <select name="al" value={formData.al} onChange={handleInputChange} className="gemini-select">
                                    {[0, 1, 2, 3, 4, 5].map(v => <option key={v} value={v}>{v}</option>)}
                                </select>
                            </div>
                            <div className="gemini-input-group">
                                <label>Sugar (0-5)</label>
                                <select name="su" value={formData.su} onChange={handleInputChange} className="gemini-select">
                                    {[0, 1, 2, 3, 4, 5].map(v => <option key={v} value={v}>{v}</option>)}
                                </select>
                            </div>
                        </div>
                        <div className="gemini-input-row">
                            <div className="gemini-input-group">
                                <label>Red Blood Cells</label>
                                <div className="gemini-toggle-group">
                                    <button type="button" className={`gemini-toggle ${formData.rbc === 'normal' ? 'active' : ''}`} onClick={() => setFormData(p => ({ ...p, rbc: 'normal' }))}>Normal</button>
                                    <button type="button" className={`gemini-toggle ${formData.rbc === 'abnormal' ? 'active' : ''}`} onClick={() => setFormData(p => ({ ...p, rbc: 'abnormal' }))}>Abnormal</button>
                                </div>
                            </div>
                            <div className="gemini-input-group">
                                <label>Pus Cell</label>
                                <div className="gemini-toggle-group">
                                    <button type="button" className={`gemini-toggle ${formData.pc === 'normal' ? 'active' : ''}`} onClick={() => setFormData(p => ({ ...p, pc: 'normal' }))}>Normal</button>
                                    <button type="button" className={`gemini-toggle ${formData.pc === 'abnormal' ? 'active' : ''}`} onClick={() => setFormData(p => ({ ...p, pc: 'abnormal' }))}>Abnormal</button>
                                </div>
                            </div>
                        </div>
                        <div className="gemini-input-row">
                            <div className="gemini-input-group">
                                <label>Pus Cell Clumps</label>
                                <div className="gemini-toggle-group">
                                    <button type="button" className={`gemini-toggle ${formData.pcc === 'notpresent' ? 'active' : ''}`} onClick={() => setFormData(p => ({ ...p, pcc: 'notpresent' }))}>Not Present</button>
                                    <button type="button" className={`gemini-toggle ${formData.pcc === 'present' ? 'active' : ''}`} onClick={() => setFormData(p => ({ ...p, pcc: 'present' }))}>Present</button>
                                </div>
                            </div>
                            <div className="gemini-input-group">
                                <label>Bacteria</label>
                                <div className="gemini-toggle-group">
                                    <button type="button" className={`gemini-toggle ${formData.ba === 'notpresent' ? 'active' : ''}`} onClick={() => setFormData(p => ({ ...p, ba: 'notpresent' }))}>Not Present</button>
                                    <button type="button" className={`gemini-toggle ${formData.ba === 'present' ? 'active' : ''}`} onClick={() => setFormData(p => ({ ...p, ba: 'present' }))}>Present</button>
                                </div>
                            </div>
                        </div>
                    </div>
                );

            case 2:
                return (
                    <div className="gemini-step-content">
                        <div className="gemini-input-row">
                            <div className="gemini-input-group">
                                <label>Blood Glucose (mg/dL)</label>
                                <input type="number" name="bgr" value={formData.bgr} onChange={handleInputChange} placeholder="e.g., 120" className="gemini-input" />
                                <span className="input-hint">Normal: 70-140</span>
                            </div>
                            <div className="gemini-input-group">
                                <label>Blood Urea (mg/dL)</label>
                                <input type="number" name="bu" value={formData.bu} onChange={handleInputChange} placeholder="e.g., 40" className="gemini-input" />
                                <span className="input-hint">Normal: 7-20</span>
                            </div>
                            <div className="gemini-input-group">
                                <label>Serum Creatinine (mg/dL)</label>
                                <input type="number" name="sc" value={formData.sc} onChange={handleInputChange} placeholder="e.g., 1.2" step="0.1" className="gemini-input" />
                                <span className="input-hint">⚠️ Key CKD indicator. Normal: 0.7-1.3</span>
                            </div>
                        </div>
                        <div className="gemini-input-row">
                            <div className="gemini-input-group">
                                <label>Sodium (mEq/L)</label>
                                <input type="number" name="sod" value={formData.sod} onChange={handleInputChange} placeholder="e.g., 140" className="gemini-input" />
                            </div>
                            <div className="gemini-input-group">
                                <label>Potassium (mEq/L)</label>
                                <input type="number" name="pot" value={formData.pot} onChange={handleInputChange} placeholder="e.g., 4.5" step="0.1" className="gemini-input" />
                            </div>
                            <div className="gemini-input-group">
                                <label>Hemoglobin (g/dL)</label>
                                <input type="number" name="hemo" value={formData.hemo} onChange={handleInputChange} placeholder="e.g., 14.0" step="0.1" className="gemini-input" />
                                <span className="input-hint">Normal: 12-17</span>
                            </div>
                        </div>
                        <div className="gemini-input-row">
                            <div className="gemini-input-group">
                                <label>Packed Cell Volume (%)</label>
                                <input type="number" name="pcv" value={formData.pcv} onChange={handleInputChange} placeholder="e.g., 44" className="gemini-input" />
                            </div>
                            <div className="gemini-input-group">
                                <label>WBC Count</label>
                                <input type="number" name="wc" value={formData.wc} onChange={handleInputChange} placeholder="e.g., 8000" className="gemini-input" />
                            </div>
                            <div className="gemini-input-group">
                                <label>RBC Count (millions/cmm)</label>
                                <input type="number" name="rc" value={formData.rc} onChange={handleInputChange} placeholder="e.g., 5.0" step="0.1" className="gemini-input" />
                            </div>
                        </div>
                    </div>
                );

            case 3:
                return (
                    <div className="gemini-step-content">
                        <div className="gemini-condition-grid">
                            {[
                                { key: 'htn', label: 'Hypertension', icon: '💓' },
                                { key: 'dm', label: 'Diabetes Mellitus', icon: '🩸' },
                                { key: 'cad', label: 'Coronary Artery Disease', icon: '❤️' },
                                { key: 'pe', label: 'Pedal Edema', icon: '🦶' },
                                { key: 'ane', label: 'Anemia', icon: '🔴' }
                            ].map(item => (
                                <div key={item.key} className="gemini-condition-card">
                                    <span className="condition-icon">{item.icon}</span>
                                    <span className="condition-label">{item.label}</span>
                                    <div className="gemini-toggle-group compact">
                                        <button type="button" className={`gemini-toggle ${formData[item.key] === 'no' ? 'active green' : ''}`} onClick={() => setFormData(p => ({ ...p, [item.key]: 'no' }))}>No</button>
                                        <button type="button" className={`gemini-toggle ${formData[item.key] === 'yes' ? 'active red' : ''}`} onClick={() => setFormData(p => ({ ...p, [item.key]: 'yes' }))}>Yes</button>
                                    </div>
                                </div>
                            ))}
                            <div className="gemini-condition-card">
                                <span className="condition-icon">🍽️</span>
                                <span className="condition-label">Appetite</span>
                                <div className="gemini-toggle-group compact">
                                    <button type="button" className={`gemini-toggle ${formData.appet === 'good' ? 'active green' : ''}`} onClick={() => setFormData(p => ({ ...p, appet: 'good' }))}>Good</button>
                                    <button type="button" className={`gemini-toggle ${formData.appet === 'poor' ? 'active red' : ''}`} onClick={() => setFormData(p => ({ ...p, appet: 'poor' }))}>Poor</button>
                                </div>
                            </div>
                        </div>
                    </div>
                );

            case 4:
                return (
                    <div className="gemini-results">
                        {loading ? (
                            <div className="gemini-loading">
                                <div className="gemini-loader">
                                    <div className="loader-ring"></div>
                                    <div className="loader-ring"></div>
                                    <div className="loader-ring"></div>
                                </div>
                                <h3>Hybrid AI Analyzing...</h3>
                                <p>Decision Tree + Random Forest + Logistic Regression</p>
                            </div>
                        ) : prediction ? (
                            <div className="gemini-results-content">
                                {/* Main Result Card */}
                                <div className={`gemini-result-card ${prediction.result === 'ckd' ? 'risk-high' : 'risk-low'}`}>
                                    <div className="result-header">
                                        {prediction.result === 'ckd' ? (
                                            <FaExclamationTriangle className="result-icon warning" />
                                        ) : (
                                            <FaCheckCircle className="result-icon success" />
                                        )}
                                        <div>
                                            <h2>{prediction.result === 'ckd' ? 'CKD Indicators Detected' : 'No CKD Indicators'}</h2>
                                            <p className="result-subtitle">Hybrid Ensemble AI Analysis</p>
                                        </div>
                                    </div>

                                    <div className="result-metrics">
                                        <div className="metric">
                                            <span className="metric-value">{prediction.confidence?.toFixed(1)}%</span>
                                            <span className="metric-label">Confidence</span>
                                        </div>
                                        <div className="metric">
                                            <span className={`metric-value risk-${prediction.risk_level?.toLowerCase()}`}>{prediction.risk_level}</span>
                                            <span className="metric-label">Risk Level</span>
                                        </div>
                                    </div>

                                    {/* Action Buttons */}
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

                                {/* Model Comparison Card */}
                                {modelDetails && (
                                    <div className="gemini-model-card">
                                        <div className="model-header">
                                            <FaBalanceScale />
                                            <h3>Hybrid Model Analysis</h3>
                                        </div>
                                        <div className="model-grid">
                                            {Object.entries(modelDetails).map(([model, details]) => (
                                                <div key={model} className="model-item">
                                                    <span className="model-name">{model.replace('_', ' ').toUpperCase()}</span>
                                                    <span className={`model-prediction ${details.prediction === 'ckd' ? 'ckd' : 'normal'}`}>
                                                        {details.prediction?.toUpperCase()}
                                                    </span>
                                                    <span className="model-confidence">{details.confidence?.toFixed(1)}%</span>
                                                    <span className="model-weight">Weight: {details.weight?.toFixed(1)}%</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* XAI Explanation */}
                                {explanation && explanation.explanation_available && (
                                    <div className="gemini-xai-card">
                                        <div className="xai-header">
                                            <FaBrain />
                                            <h3>Explainable AI (SHAP)</h3>
                                        </div>
                                        <p className="xai-description">{explanation.text_explanation}</p>

                                        {explanation.feature_importance && (
                                            <div className="xai-features">
                                                <h4>Contributing Factors</h4>
                                                {explanation.feature_importance.slice(0, 6).map((feat, idx) => (
                                                    <div key={idx} className="xai-feature-item">
                                                        <div className="feature-info">
                                                            <span className="feature-name">{feat.feature?.toUpperCase()}</span>
                                                            <span className="feature-value">Value: {feat.raw_value}</span>
                                                        </div>
                                                        <span className={`feature-impact ${feat.direction === 'increases' ? 'negative' : 'positive'}`}>
                                                            {feat.direction === 'increases' ? '↑ Risk' : '↓ Risk'}
                                                        </span>
                                                    </div>
                                                ))}
                                            </div>
                                        )}

                                        {/* Clinical Insights */}
                                        {explanation.clinical_insights && explanation.clinical_insights.length > 0 && (
                                            <div className="xai-insights">
                                                <h4>Clinical Insights</h4>
                                                {explanation.clinical_insights.map((insight, idx) => (
                                                    <div key={idx} className={`insight-item ${insight.severity}`}>
                                                        <span className="insight-feature">{insight.feature?.toUpperCase()}</span>
                                                        <span className="insight-text">{insight.insight}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                )}

                                {/* Recommendations */}
                                {recommendations && (
                                    <div className="gemini-recommendations-card">
                                        <div className="rec-header">
                                            <FaAppleAlt />
                                            <h3>Personalized Recommendations</h3>
                                        </div>

                                        <div className="rec-tabs">
                                            <div className="rec-tab-content">
                                                <div className="rec-section">
                                                    <h4>🥗 Diet Guidelines</h4>
                                                    <div className="rec-columns">
                                                        <div className="rec-column good">
                                                            <h5>✅ Recommended</h5>
                                                            <ul>
                                                                {recommendations.diet?.foods_to_eat?.slice(0, 4).map((food, idx) => (
                                                                    <li key={idx}>{food}</li>
                                                                ))}
                                                            </ul>
                                                        </div>
                                                        <div className="rec-column avoid">
                                                            <h5>⚠️ Limit</h5>
                                                            <ul>
                                                                {recommendations.diet?.foods_to_limit?.slice(0, 4).map((food, idx) => (
                                                                    <li key={idx}>{food}</li>
                                                                ))}
                                                            </ul>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="rec-section">
                                                    <h4>💪 Lifestyle Changes</h4>
                                                    <div className="lifestyle-chips">
                                                        {recommendations.lifestyle?.slice(0, 6).map((item, idx) => (
                                                            <span key={idx} className="lifestyle-chip">{item}</span>
                                                        ))}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* Quick Actions */}
                                <div className="quick-actions">
                                    <button className="gemini-btn secondary" onClick={resetForm}>
                                        Start New Assessment
                                    </button>
                                </div>
                            </div>
                        ) : null}
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <div className="gemini-container">
            <div className="gemini-header">
                <div className="gemini-title">
                    <FaFlask className="title-icon" />
                    <div>
                        <h1>CKD Risk Assessment</h1>
                        <p>Hybrid AI with Explainable Results (DT + RF + LR)</p>
                    </div>
                </div>
            </div>

            {/* Progress Steps */}
            {currentStep < 4 && (
                <div className="gemini-progress">
                    {steps.slice(0, 4).map((step, index) => (
                        <div
                            key={index}
                            className={`gemini-step ${index === currentStep ? 'active' : ''} ${index < currentStep ? 'completed' : ''}`}
                            onClick={() => index < currentStep && setCurrentStep(index)}
                        >
                            <div className="step-indicator">
                                {index < currentStep ? <FaCheckCircle /> : <span>{step.icon}</span>}
                            </div>
                            <div className="step-info">
                                <span className="step-title">{step.title}</span>
                                <span className="step-desc">{step.description}</span>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Form Content */}
            <div className="gemini-form-container">
                {renderStepContent()}
            </div>

            {/* Navigation Buttons */}
            {currentStep < 4 && (
                <div className="gemini-nav">
                    <button
                        className="gemini-btn secondary"
                        onClick={prevStep}
                        disabled={currentStep === 0}
                    >
                        <FaChevronLeft /> Previous
                    </button>

                    {currentStep < 3 ? (
                        <button className="gemini-btn primary" onClick={nextStep}>
                            Next <FaChevronRight />
                        </button>
                    ) : (
                        <button className="gemini-btn primary analyze" onClick={handleAnalyze}>
                            <FaBrain /> Analyze with Hybrid AI
                        </button>
                    )}
                </div>
            )}
        </div>
    );
};

export default CKDTestForm;
