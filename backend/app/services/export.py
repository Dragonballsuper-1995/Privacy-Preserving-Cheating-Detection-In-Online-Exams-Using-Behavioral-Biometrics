"""
Advanced Export Service

Provides PDF, CSV, and JSON export capabilities for analysis reports.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from io import BytesIO
import json
import csv

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab not installed. Install with: pip install reportlab")


class ExportService:
    """Service for exporting analysis data in various formats."""
    
    @staticmethod
    def export_to_json(
        session_data: Dict[str, Any],
        include_events: bool = False
    ) -> str:
        """
        Export session data to JSON.
        
        Args:
            session_data: Session analysis data
            include_events: Whether to include raw events
            
        Returns:
            JSON string
        """
        export_data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "session": session_data
        }
        
        if not include_events and "events" in export_data["session"]:
            del export_data["session"]["events"]
        
        return json.dumps(export_data, indent=2)
    
    @staticmethod
    def export_to_csv(
        sessions: List[Dict[str, Any]],
        include_features: bool = False
    ) -> str:
        """
        Export multiple sessions to CSV format.
        
        Args:
            sessions: List of session data dictionaries
            include_features: Whether to include detailed features
            
        Returns:
            CSV string
        """
        if not sessions:
            return ""
        
        output = BytesIO()
        writer = csv.writer(output)
        
        # Define headers
        headers = [
            "session_id",
            "student_id",
            "exam_id",
            "start_time",
            "end_time",
            "risk_score",
            "risk_level",
            "is_flagged"
        ]
        
        if include_features:
            # Add feature columns (sample, adjust based on actual features)
            headers.extend([
                "paste_count",
                "blur_count",
                "typing_speed",
                "backspace_ratio"
            ])
        
        writer.writerow(headers)
        
        # Write data rows
        for session in sessions:
            row = [
                session.get("session_id", ""),
                session.get("student_id", ""),
                session.get("exam_id", ""),
                session.get("start_time", ""),
                session.get("end_time", ""),
                session.get("risk_score", 0.0),
                session.get("risk_level", ""),
                session.get("is_flagged", False)
            ]
            
            if include_features and "features" in session:
                features = session["features"]
                row.extend([
                    features.get("paste_count", 0),
                    features.get("blur_count", 0),
                    features.get("typing_speed", 0.0),
                    features.get("backspace_ratio", 0.0)
                ])
            
            writer.writerow(row)
        
        return output.getvalue().decode('utf-8')
    
    @staticmethod
    def export_to_pdf(
        session_data: Dict[str, Any],
        include_explanation: bool = True
    ) -> bytes:
        """
        Export session analysis to PDF report.
        
        Args:
            session_data: Session analysis data
            include_explanation: Whether to include explanation
            
        Returns:
            PDF bytes
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF export. Install with: pip install reportlab")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30
        )
        
        story.append(Paragraph("Cheating Detection Analysis Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Session Information
        story.append(Paragraph("Session Information", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        session_info = [
            ["Session ID:", session_data.get("session_id", "N/A")],
            ["Student ID:", session_data.get("student_id", "N/A")],
            ["Exam ID:", session_data.get("exam_id", "N/A")],
            ["Start Time:", session_data.get("start_time", "N/A")],
            ["End Time:", session_data.get("end_time", "N/A")]
        ]
        
        info_table = Table(session_info, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Risk Assessment
        story.append(Paragraph("Risk Assessment", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        risk_score = session_data.get("risk_score", 0.0)
        risk_level = session_data.get("risk_level", "unknown")
        is_flagged = session_data.get("is_flagged", False)
        
        # Determine color based on risk level
        risk_color = {
            "low": colors.green,
            "medium": colors.orange,
            "high": colors.red,
            "critical": colors.darkred
        }.get(risk_level.lower(), colors.grey)
        
        risk_data = [
            ["Risk Score:", f"{risk_score:.2%}"],
            ["Risk Level:", risk_level.upper()],
            ["Flagged:", "YES" if is_flagged else "NO"]
        ]
        
        risk_table = Table(risk_data, colWidths=[2*inch, 4*inch])
        risk_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (1, 1), (1, 1), risk_color),
            ('TEXTCOLOR', (1, 1), (1, 1), colors.white),
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('FONT', (1, 1), (1, 1), 'Helvetica-Bold', 12)
        ]))
        
        story.append(risk_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Risk Factors
        if "risk_factors" in session_data and session_data["risk_factors"]:
            story.append(Paragraph("Risk Factors Identified", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            for factor in session_data["risk_factors"]:
                story.append(Paragraph(f"• {factor}", styles['Normal']))
            
            story.append(Spacer(1, 0.3*inch))
        
        # Explanation
        if include_explanation and "explanation" in session_data:
            story.append(Paragraph("Detailed Explanation", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            explanation_text = session_data["explanation"].replace("\n", "<br/>")
            story.append(Paragraph(explanation_text, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Features Summary (if available)
        if "features" in session_data:
            story.append(PageBreak())
            story.append(Paragraph("Behavioral Features Summary", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            features = session_data["features"]
            feature_data = [["Feature", "Value"]]
            
            for key, value in features.items():
                if isinstance(value, (int, float)):
                    feature_data.append([key, f"{value:.2f}" if isinstance(value, float) else str(value)])
            
            if len(feature_data) > 1:
                feature_table = Table(feature_data, colWidths=[3*inch, 2*inch])
                feature_table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                    ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                
                story.append(feature_table)
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer_text = f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        story.append(Paragraph(footer_text, styles['Italic']))
        
        # Build PDF
        doc.build(story)
        
        return buffer.getvalue()
    
    @staticmethod
    def export_batch_summary(
        sessions: List[Dict[str, Any]],
        exam_id: str
    ) -> bytes:
        """
        Export summary report for multiple sessions (exam-level).
        
        Args:
            sessions: List of session data
            exam_id: Exam identifier
            
        Returns:
            PDF bytes
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab required")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        story.append(Paragraph(f"Exam Analysis Report: {exam_id}", styles['Title']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary statistics
        total = len(sessions)
        flagged = sum(1 for s in sessions if s.get("is_flagged", False))
        avg_risk = sum(s.get("risk_score", 0.0) for s in sessions) / total if total > 0 else 0.0
        
        summary_data = [
            ["Total Sessions:", str(total)],
            ["Flagged Sessions:", str(flagged)],
            ["Flagging Rate:", f"{(flagged/total*100):.1f}%" if total > 0 else "N/A"],
            ["Average Risk Score:", f"{avg_risk:.2%}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 11)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.4*inch))
        
        # Build PDF
        doc.build(story)
        
        return buffer.getvalue()
