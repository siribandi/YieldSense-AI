import os
import sys
import io
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db.models import User, Farm, Crop, Prediction


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render 'Page X of Y' on every page."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header rule & title
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(40, 755, 570, 755)
        self.drawString(40, 760, "YieldSense AI -- Platform Farmer & Intelligence Audit Report")
        self.drawRightString(570, 760, "CONFIDENTIAL & PROPRIETARY")

        # Footer rule & page number
        self.line(40, 45, 570, 45)
        self.drawString(40, 32, "YieldSense AI Platform (c) 2026 | Agricultural Intelligence & Crop Forecasting")
        self.drawRightString(570, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


class ReportService:
    """
    Generates professional, high-fidelity PDF intelligence reports
    summarizing Farmer records, holdings, crops, and yield predictions.
    """

    def generate_farmer_records_pdf(self, db: Session) -> bytes:
        """
        Queries real PostgreSQL database records and builds a beautifully styled PDF document.
        """
        # 1. Fetch Real Database Data
        users = db.query(User).order_by(User.role.asc(), User.created_at.desc()).all()
        farms = db.query(Farm).all()
        crops = db.query(Crop).all()
        predictions = db.query(Prediction).order_by(Prediction.created_at.desc()).all()

        total_users = len(users)
        total_farmers = sum(1 for u in users if u.role == "Farmer")
        total_admins = sum(1 for u in users if u.role == "Administrator")
        total_farms = len(farms)
        total_crops = len(crops)
        total_predictions = len(predictions)
        avg_yield = round(float(sum(p.predicted_yield_kg for p in predictions) / total_predictions), 1) if total_predictions > 0 else 0.0

        # 2. Build Document Flowable Elements
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=40,
            rightMargin=40,
            topMargin=55,
            bottomMargin=55
        )

        styles = getSampleStyleSheet()
        
        # Custom Typography Styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#1b5e20'),
            spaceAfter=2
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#475569'),
            spaceAfter=12
        )
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#0f172a'),
            spaceBefore=14,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'DocBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor('#334155')
        )
        body_bold = ParagraphStyle(
            'DocBodyBold',
            parent=body_style,
            fontName='Helvetica-Bold'
        )
        table_hdr_style = ParagraphStyle(
            'TableHdr',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.white
        )
        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#1e293b')
        )
        table_cell_bold = ParagraphStyle(
            'TableCellBold',
            parent=table_cell_style,
            fontName='Helvetica-Bold'
        )
        badge_style = ParagraphStyle(
            'BadgeStyle',
            parent=table_cell_style,
            fontName='Helvetica-Bold',
            fontSize=7.5,
            textColor=colors.HexColor('#1b5e20')
        )

        story = []

        # --- Document Header ---
        story.append(Paragraph("YieldSense AI -- Farmer Records & System Intelligence Report", title_style))
        gen_time = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
        story.append(Paragraph(f"Official Administrator Audit Report | Generated on: <b>{gen_time}</b>", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2e7d32"), spaceAfter=12))

        # --- Section 1: Executive KPI Summary Box ---
        story.append(Paragraph("1. Executive Platform Telemetry", section_style))

        kpi_data = [
            [
                Paragraph("<b>Total Registered Users</b>", table_cell_bold),
                Paragraph(f"<b>{total_users}</b> ({total_farmers} Farmers, {total_admins} Admins)", table_cell_style),
                Paragraph("<b>Total Farm Fields</b>", table_cell_bold),
                Paragraph(f"<b>{total_farms}</b> registered farms", table_cell_style)
            ],
            [
                Paragraph("<b>Total Logged Crops</b>", table_cell_bold),
                Paragraph(f"<b>{total_crops}</b> crop entries", table_cell_style),
                Paragraph("<b>Yield Predictions Run</b>", table_cell_bold),
                Paragraph(f"<b>{total_predictions}</b> ML forecasts", table_cell_style)
            ],
            [
                Paragraph("<b>Avg Predicted Yield</b>", table_cell_bold),
                Paragraph(f"<b>{avg_yield:,.1f}</b> kg / acre", table_cell_style),
                Paragraph("<b>Active ML Model</b>", table_cell_bold),
                Paragraph("<b>Linear Regression v2.0.0</b> (R2: 0.0029, MAE: 4,273)", table_cell_style)
            ]
        ]
        kpi_table = Table(kpi_data, colWidths=[120, 145, 120, 145])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 12))

        # --- Section 2: Complete Farmer & User Directory ---
        story.append(Paragraph("2. Farmer & User Master Directory", section_style))

        user_table_data = [
            [
                Paragraph("ID", table_hdr_style),
                Paragraph("Farmer / User Name", table_hdr_style),
                Paragraph("Email Address", table_hdr_style),
                Paragraph("Role", table_hdr_style),
                Paragraph("Farms", table_hdr_style),
                Paragraph("Crops", table_hdr_style),
                Paragraph("Predictions", table_hdr_style),
                Paragraph("Registration Date", table_hdr_style),
                Paragraph("Status", table_hdr_style),
            ]
        ]

        for u in users:
            u_farms = len(u.farms)
            u_crops = sum(len(f.crops) for f in u.farms)
            u_preds = len(u.predictions)
            status_text = "Active" if (u_preds > 0 or u_farms > 0) else "Registered"
            reg_date = u.created_at.strftime("%Y-%m-%d") if u.created_at else "N/A"

            user_table_data.append([
                Paragraph(f"#{u.id}", table_cell_style),
                Paragraph(f"<b>{u.name}</b>", table_cell_style),
                Paragraph(u.email, table_cell_style),
                Paragraph(u.role, badge_style if u.role == "Farmer" else table_cell_bold),
                Paragraph(str(u_farms), table_cell_style),
                Paragraph(str(u_crops), table_cell_style),
                Paragraph(str(u_preds), table_cell_style),
                Paragraph(reg_date, table_cell_style),
                Paragraph(status_text, table_cell_bold if status_text == "Active" else table_cell_style),
            ])

        user_table = Table(
            user_table_data,
            colWidths=[24, 95, 125, 52, 32, 32, 54, 66, 52]
        )
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1b5e20')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(user_table)
        story.append(Spacer(1, 14))

        # --- Section 3: Detailed Farmer Holdings & Prediction Logs ---
        story.append(Paragraph("3. Detailed Farmer Holdings & Recent Yield Forecasts", section_style))

        # Only list farmers
        farmers = [u for u in users if u.role == "Farmer"]
        if not farmers:
            story.append(Paragraph("<i>No registered farmer accounts found.</i>", body_style))
        else:
            for farmer in farmers:
                farmer_block = []
                farmer_block.append(Paragraph(
                    f"<b>Farmer #{farmer.id}: {farmer.name}</b> ({farmer.email}) -- Registered: {farmer.created_at.strftime('%Y-%m-%d') if farmer.created_at else 'N/A'}",
                    ParagraphStyle('FarmerSub', parent=body_bold, textColor=colors.HexColor('#1e40af'), fontSize=9.5)
                ))
                
                # Farms list
                if farmer.farms:
                    farm_details = []
                    for f in farmer.farms:
                        crops_str = ", ".join([c.crop_name for c in f.crops]) if f.crops else "None logged"
                        farm_details.append(f"• <b>{f.farm_name}</b>: {f.area} acres ({f.soil_type} soil, {f.location}) -- Crops: {crops_str}")
                    farmer_block.append(Paragraph("<br/>".join(farm_details), body_style))
                else:
                    farmer_block.append(Paragraph("<i>No farm parcels registered yet.</i>", body_style))

                # Latest Predictions
                if farmer.predictions:
                    pred_rows = [
                        [
                            Paragraph("Date", table_hdr_style),
                            Paragraph("Crop", table_hdr_style),
                            Paragraph("State", table_hdr_style),
                            Paragraph("Soil / Fert", table_hdr_style),
                            Paragraph("Rain (mm)", table_hdr_style),
                            Paragraph("pH", table_hdr_style),
                            Paragraph("Predicted Yield", table_hdr_style),
                        ]
                    ]
                    for p in farmer.predictions[:5]:  # show up to 5 latest
                        pred_rows.append([
                            Paragraph(p.created_at.strftime("%Y-%m-%d"), table_cell_style),
                            Paragraph(f"<b>{p.crop}</b>", table_cell_style),
                            Paragraph(p.state, table_cell_style),
                            Paragraph(f"{p.soil_type} / {p.fertilizer}", table_cell_style),
                            Paragraph(f"{p.rainfall_mm:.0f}", table_cell_style),
                            Paragraph(f"{p.soil_ph:.2f}", table_cell_style),
                            Paragraph(f"<b>{p.predicted_yield_kg:,.1f} kg/ac</b>", table_cell_bold),
                        ])
                    p_table = Table(pred_rows, colWidths=[65, 65, 80, 110, 50, 45, 115])
                    p_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                        ('LEFTPADDING', (0, 0), (-1, -1), 4),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    farmer_block.append(Spacer(1, 4))
                    farmer_block.append(p_table)
                else:
                    farmer_block.append(Paragraph("<i>No yield prediction forecasts run yet.</i>", body_style))

                farmer_block.append(Spacer(1, 8))
                story.append(KeepTogether(farmer_block))

        # Build PDF with NumberedCanvas
        doc.build(story, canvasmaker=NumberedCanvas)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
