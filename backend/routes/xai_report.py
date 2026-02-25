"""
XAI Clinical Report Generator - PDF Generation
Generates doctor-ready and patient-friendly PDF reports with SHAP explanations
"""

from flask import Blueprint, request, jsonify, send_file, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId
import os
import io

xai_report_bp = Blueprint('xai_report', __name__)

# Try to import PDF libraries
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: ReportLab not installed. Install with: pip install reportlab")


def generate_pdf_report(prediction_data, patient_info):
    """Generate a comprehensive PDF clinical report"""
    
    if not REPORTLAB_AVAILABLE:
        return None, "ReportLab not installed"
    
    try:
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                               rightMargin=50, leftMargin=50,
                               topMargin=50, bottomMargin=50)
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        section_title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f2937'),
            spaceBefore=20,
            spaceAfter=10
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
            spaceAfter=6
        )
        
        risk_high_style = ParagraphStyle(
            'RiskHigh',
            parent=styles['Normal'],
            fontSize=18,
            textColor=colors.HexColor('#dc2626'),
            alignment=TA_CENTER,
            spaceBefore=10,
            spaceAfter=10
        )
        
        risk_low_style = ParagraphStyle(
            'RiskLow',
            parent=styles['Normal'],
            fontSize=18,
            textColor=colors.HexColor('#16a34a'),
            alignment=TA_CENTER,
            spaceBefore=10,
            spaceAfter=10
        )
        
        # Build content
        content = []
        
        # Header
        content.append(Paragraph("CKD Clinical Report", title_style))
        content.append(Paragraph("Explainable AI-Powered Chronic Kidney Disease Assessment", subtitle_style))
        content.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3b82f6')))
        content.append(Spacer(1, 20))
        
        # Report Info
        report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        report_id = prediction_data.get('prediction_id', 'N/A')
        
        info_data = [
            ['Report Date:', report_date],
            ['Report ID:', report_id[:20] + '...' if len(str(report_id)) > 20 else report_id],
            ['Patient Name:', patient_info.get('name', 'N/A')],
            ['Age:', f"{prediction_data.get('input_data', {}).get('age', 'N/A')} years"],
        ]
        
        info_table = Table(info_data, colWidths=[120, 350])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        content.append(info_table)
        content.append(Spacer(1, 20))
        
        # Prediction Result Section
        content.append(Paragraph("CKD Prediction Result", section_title_style))
        content.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        
        pred = prediction_data.get('prediction', {})
        result = pred.get('result', 'unknown').upper()
        confidence = pred.get('confidence', 0)
        risk_level = pred.get('risk_level', 'Unknown')
        
        # Result box
        if result == 'CKD':
            result_text = f"WARNING: CKD INDICATORS DETECTED"
            result_style = risk_high_style
        else:
            result_text = f"CLEAR: NO CKD INDICATORS DETECTED"
            result_style = risk_low_style
        
        content.append(Paragraph(result_text, result_style))
        
        # Metrics table
        metrics_data = [
            ['Metric', 'Value'],
            ['Prediction', 'CKD Detected' if result == 'CKD' else 'No CKD'],
            ['Confidence Score', f"{confidence:.1f}%"],
            ['Risk Level', risk_level],
            ['Model Type', 'Hybrid Ensemble (DT + RF + LR)']
        ]
        
        metrics_table = Table(metrics_data, colWidths=[200, 270])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))
        content.append(Spacer(1, 10))
        content.append(metrics_table)
        content.append(Spacer(1, 20))
        
        # Model Comparison Section
        model_details = prediction_data.get('model_details', {})
        if model_details:
            content.append(Paragraph("Hybrid Model Analysis", section_title_style))
            content.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
            
            model_data = [
                ['Model', 'Prediction', 'Confidence', 'Weight']
            ]
            
            for model_name, details in model_details.items():
                formatted_name = model_name.replace('_', ' ').title()
                model_data.append([
                    formatted_name,
                    details.get('prediction', 'N/A').upper(),
                    f"{details.get('confidence', 0):.1f}%",
                    f"{details.get('weight', 0):.1f}%"
                ])
            
            model_table = Table(model_data, colWidths=[140, 100, 100, 100])
            model_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#faf5ff')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ]))
            content.append(Spacer(1, 10))
            content.append(model_table)
            content.append(Spacer(1, 20))
        
        # XAI Explanation Section
        xai = prediction_data.get('xai_explanation', {})
        if xai.get('explanation_available'):
            content.append(Paragraph("Explainable AI Analysis", section_title_style))
            content.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
            
            # Text explanation
            text_exp = xai.get('text_explanation', '')
            if text_exp:
                content.append(Spacer(1, 10))
                content.append(Paragraph(f"<b>AI Reasoning:</b> {text_exp}", normal_style))
                content.append(Spacer(1, 10))
            
            # Feature importance table
            features = xai.get('feature_importance', [])
            if features:
                content.append(Paragraph("<b>Top Contributing Factors:</b>", normal_style))
                
                feature_data = [['Feature', 'Value', 'Impact', 'Direction']]
                for f in features[:8]:
                    direction_text = "↑ Increases Risk" if f.get('direction') == 'increases' else "↓ Decreases Risk"
                    feature_data.append([
                        f.get('feature', '').upper(),
                        str(f.get('raw_value', 'N/A')),
                        f"{f.get('impact', 0):.4f}",
                        direction_text
                    ])
                
                feature_table = Table(feature_data, colWidths=[80, 80, 80, 130])
                feature_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0ea5e9')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f9ff')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                ]))
                content.append(Spacer(1, 10))
                content.append(feature_table)
            
            # Clinical insights
            insights = xai.get('clinical_insights', [])
            if insights:
                content.append(Spacer(1, 15))
                content.append(Paragraph("<b>Clinical Insights:</b>", normal_style))
                for insight in insights[:5]:
                    icon = "[!]" if insight.get('severity') == 'warning' else "[OK]"
                    content.append(Paragraph(
                        f"{icon} <b>{insight.get('feature', '').upper()}:</b> {insight.get('insight', '')}",
                        normal_style
                    ))
        
        content.append(Spacer(1, 20))
        
        # Medical Parameters Section
        content.append(Paragraph("Medical Parameters Analyzed", section_title_style))
        content.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        
        input_data = prediction_data.get('input_data', {})
        param_data = [
            ['Parameter', 'Value', 'Parameter', 'Value']
        ]
        
        params = list(input_data.items())
        for i in range(0, len(params), 2):
            row = []
            row.extend([params[i][0].upper(), str(params[i][1])])
            if i + 1 < len(params):
                row.extend([params[i+1][0].upper(), str(params[i+1][1])])
            else:
                row.extend(['', ''])
            param_data.append(row)
        
        param_table = Table(param_data, colWidths=[100, 100, 100, 100])
        param_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6b7280')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        content.append(Spacer(1, 10))
        content.append(param_table)
        
        # Disclaimer Section
        content.append(Spacer(1, 30))
        content.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#fbbf24')))
        
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#92400e'),
            alignment=TA_CENTER,
            spaceBefore=10,
            spaceAfter=10
        )
        
        disclaimer_text = """
        <b>IMPORTANT MEDICAL DISCLAIMER</b><br/><br/>
        This report is generated by an AI-powered Clinical Decision Support System and is intended for 
        informational purposes only. It is NOT a medical diagnosis. This system is designed to assist 
        healthcare professionals in their clinical decision-making process.<br/><br/>
        <b>Always consult a qualified nephrologist or healthcare provider for proper diagnosis, treatment, 
        and medical advice.</b> Do not make any medical decisions based solely on this AI-generated report.
        """
        content.append(Paragraph(disclaimer_text, disclaimer_style))
        
        # Footer
        content.append(Spacer(1, 20))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#9ca3af'),
            alignment=TA_CENTER
        )
        content.append(Paragraph(
            f"Generated by CKD Predictor - Explainable AI System | {report_date}",
            footer_style
        ))
        
        # Build PDF
        doc.build(content)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes, None
        
    except Exception as e:
        return None, str(e)


@xai_report_bp.route('/pdf/<prediction_id>', methods=['GET'])
@jwt_required()
def download_report(prediction_id):
    """Generate and download PDF report for a prediction"""
    try:
        from app import db
        import json as json_lib
        current_user = get_jwt_identity()
        
        # Handle identity as dict, JSON string, or plain string
        if isinstance(current_user, dict):
            user_email = current_user.get('email', '')
            jwt_name = current_user.get('name', 'Unknown')
        elif isinstance(current_user, str) and current_user.startswith('{'):
            # It's a JSON string, parse it
            try:
                user_data = json_lib.loads(current_user)
                user_email = user_data.get('email', '')
                jwt_name = user_data.get('name', 'Unknown')
            except:
                user_email = current_user
                jwt_name = 'Unknown'
        else:
            user_email = current_user
            jwt_name = 'Unknown'
        
        # Get prediction
        prediction = db.hybrid_predictions.find_one({'_id': ObjectId(prediction_id)})
        
        if not prediction:
            # Try regular predictions collection
            prediction = db.ckd_predictions.find_one({'_id': ObjectId(prediction_id)})
        
        if not prediction:
            return jsonify({
                'success': False,
                'message': 'Prediction not found'
            }), 404
        
        # Get patient info from database (priority) or JWT
        user = None
        if user_email:
            user = db.users.find_one({'email': user_email})
        
        # Determine the best name to use
        if user and user.get('name'):
            patient_name = user.get('name')
        elif jwt_name and jwt_name != 'Unknown':
            patient_name = jwt_name
        else:
            patient_name = user_email or 'Unknown Patient'
        
        patient_info = {
            'name': patient_name,
            'email': user_email
        }
        
        # Add prediction_id to data
        prediction['prediction_id'] = str(prediction['_id'])
        
        # Generate PDF
        pdf_bytes, error = generate_pdf_report(prediction, patient_info)
        
        if error:
            return jsonify({
                'success': False,
                'message': f'Error generating PDF: {error}'
            }), 500
        
        # Save report metadata
        report_record = {
            'prediction_id': prediction_id,
            'user_id': user_email,
            'generated_at': datetime.utcnow(),
            'report_type': 'clinical_xai'
        }
        db.xai_reports.insert_one(report_record)
        
        # Return PDF with proper headers
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=CKD_Report_{prediction_id[:8]}.pdf'
        response.headers['Content-Length'] = len(pdf_bytes)
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@xai_report_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_report_from_data():
    """Generate PDF report from prediction data (without saving prediction first)"""
    try:
        from app import db
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Handle identity as dict, JSON string, or plain string
        if isinstance(current_user, dict):
            user_email = current_user.get('email', '')
            jwt_name = current_user.get('name', 'Unknown')
        elif isinstance(current_user, str) and current_user.startswith('{'):
            # It's a JSON string, parse it
            try:
                import json as json_lib
                user_data = json_lib.loads(current_user)
                user_email = user_data.get('email', '')
                jwt_name = user_data.get('name', 'Unknown')
            except:
                user_email = current_user
                jwt_name = 'Unknown'
        else:
            user_email = current_user
            jwt_name = 'Unknown'
        
        # Get patient info from database (priority) or JWT
        user = None
        if user_email:
            user = db.users.find_one({'email': user_email})
        
        # Determine the best name to use
        if user and user.get('name'):
            patient_name = user.get('name')
        elif jwt_name and jwt_name != 'Unknown':
            patient_name = jwt_name
        else:
            patient_name = user_email or 'Unknown Patient'
        
        patient_info = {
            'name': patient_name,
            'email': user_email
        }
        
        # Ensure prediction_id exists
        if 'prediction_id' not in data:
            data['prediction_id'] = f"TEMP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Generate PDF
        pdf_bytes, error = generate_pdf_report(data, patient_info)
        
        if error:
            return jsonify({
                'success': False,
                'message': f'Error generating PDF: {error}'
            }), 500
        
        # Return PDF with proper headers
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=CKD_Clinical_Report.pdf'
        response.headers['Content-Length'] = len(pdf_bytes)
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@xai_report_bp.route('/history', methods=['GET'])
@jwt_required()
def get_report_history():
    """Get user's report generation history"""
    try:
        from app import db
        current_user = get_jwt_identity()
        
        reports = list(db.xai_reports.find(
            {'user_id': current_user}
        ).sort('generated_at', -1).limit(20))
        
        for report in reports:
            report['_id'] = str(report['_id'])
            if report.get('generated_at'):
                report['generated_at'] = report['generated_at'].isoformat()
        
        return jsonify({
            'success': True,
            'reports': reports,
            'count': len(reports)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@xai_report_bp.route('/share', methods=['POST'])
@jwt_required()
def share_report():
    """Share CKD report via email using Gmail SMTP"""
    try:
        from app import db
        import json as json_lib
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.application import MIMEApplication
        
        current_user = get_jwt_identity()
        data = request.get_json()
        
        prediction_id = data.get('prediction_id')
        recipient_email = data.get('recipient_email')
        patient_name = data.get('patient_name', 'Patient')
        
        if not prediction_id or not recipient_email:
            return jsonify({
                'success': False,
                'message': 'Prediction ID and recipient email are required'
            }), 400
        
        # Get user info
        if isinstance(current_user, dict):
            user_email = current_user.get('email', '')
        elif isinstance(current_user, str) and current_user.startswith('{'):
            try:
                user_data = json_lib.loads(current_user)
                user_email = user_data.get('email', '')
            except:
                user_email = current_user
        else:
            user_email = current_user
        
        # Get the prediction
        prediction = db.hybrid_predictions.find_one({'_id': ObjectId(prediction_id)})
        if not prediction:
            prediction = db.ckd_predictions.find_one({'_id': ObjectId(prediction_id)})
        
        if not prediction:
            return jsonify({
                'success': False,
                'message': 'Prediction not found'
            }), 404
        
        # Gmail SMTP Configuration
        smtp_host = 'smtp.gmail.com'
        smtp_port = 587
        smtp_user = 'sagarbawankule334@gmail.com'
        smtp_pass = 'tocivdwjfniqeyad'
        
        # Log the share action
        share_record = {
            'prediction_id': prediction_id,
            'shared_by': user_email,
            'shared_to': recipient_email,
            'patient_name': patient_name,
            'shared_at': datetime.utcnow(),
            'share_method': 'email',
            'status': 'pending'
        }
        
        try:
            # Generate PDF
            user_info = db.users.find_one({'email': user_email})
            patient_info = {
                'name': user_info.get('name', patient_name) if user_info else patient_name,
                'email': user_email
            }
            prediction['prediction_id'] = str(prediction['_id'])
            pdf_bytes, error = generate_pdf_report(prediction, patient_info)
            
            if not pdf_bytes:
                return jsonify({
                    'success': False,
                    'message': f'Failed to generate PDF: {error}'
                }), 500
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = f'CKD Prediction System <{smtp_user}>'
            msg['To'] = recipient_email
            msg['Subject'] = f'CKD Screening Report - {patient_name}'
            
            # Email body
            pred_result = prediction.get('prediction', {})
            result_text = 'CKD Detected' if pred_result.get('result') == 'ckd' else 'No CKD Detected'
            risk_level = pred_result.get('risk_level', 'N/A')
            confidence = pred_result.get('confidence', 0)
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center;">
                        <h1 style="margin: 0;">🏥 CKD Screening Report</h1>
                        <p style="margin: 5px 0 0;">Explainable AI-Powered Assessment</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border: 1px solid #e9ecef;">
                        <p>Dear Recipient,</p>
                        <p>Please find attached the CKD (Chronic Kidney Disease) screening report for <strong>{patient_name}</strong>.</p>
                        
                        <div style="background: white; border-radius: 8px; padding: 15px; margin: 20px 0; border-left: 4px solid {'#dc3545' if pred_result.get('result') == 'ckd' else '#28a745'};">
                            <h3 style="margin: 0 0 10px; color: #333;">📊 Report Summary</h3>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Result:</strong></td>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eee; color: {'#dc3545' if pred_result.get('result') == 'ckd' else '#28a745'}; font-weight: bold;">{result_text}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Risk Level:</strong></td>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{risk_level}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Confidence:</strong></td>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{confidence:.1f}%</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0;"><strong>Date:</strong></td>
                                    <td style="padding: 8px 0;">{datetime.now().strftime('%B %d, %Y')}</td>
                                </tr>
                            </table>
                        </div>
                        
                        <p>📎 <strong>The detailed PDF report is attached to this email.</strong></p>
                        
                        <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 5px; padding: 15px; margin-top: 20px;">
                            <p style="margin: 0; color: #856404;"><strong>⚠️ Important:</strong> This report is generated by an AI-powered Clinical Decision Support System and is for informational purposes only. Please consult a qualified healthcare provider for proper diagnosis and treatment.</p>
                        </div>
                    </div>
                    
                    <div style="background: #333; color: white; padding: 15px; border-radius: 0 0 10px 10px; text-align: center; font-size: 12px;">
                        <p style="margin: 0;">Generated by CKD Prediction System</p>
                        <p style="margin: 5px 0 0; color: #aaa;">Explainable AI-Based Chronic Kidney Disease Assessment</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Attach PDF
            pdf_attachment = MIMEApplication(pdf_bytes, _subtype='pdf')
            pdf_attachment.add_header('Content-Disposition', 'attachment', 
                                    filename=f'CKD_Report_{prediction_id[:8]}.pdf')
            msg.attach(pdf_attachment)
            
            # Send email via Gmail SMTP
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            
            share_record['status'] = 'sent'
            db.report_shares.insert_one(share_record)
            
            return jsonify({
                'success': True,
                'message': f'Report successfully sent to {recipient_email}',
                'method': 'email'
            })
                
        except smtplib.SMTPAuthenticationError as auth_error:
            share_record['status'] = 'failed'
            share_record['error'] = 'SMTP Authentication failed'
            db.report_shares.insert_one(share_record)
            return jsonify({
                'success': False,
                'message': 'Email authentication failed. Please check SMTP credentials.'
            }), 500
            
        except smtplib.SMTPException as smtp_error:
            share_record['status'] = 'failed'
            share_record['error'] = str(smtp_error)
            db.report_shares.insert_one(share_record)
            return jsonify({
                'success': False,
                'message': f'Failed to send email: {str(smtp_error)}'
            }), 500
        
    except Exception as e:
        print(f"Share report error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
