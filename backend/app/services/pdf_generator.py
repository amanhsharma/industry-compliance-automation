import io
from datetime import datetime, timezone
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_compliance_pdf_report(
    tenant_name: str,
    summary_data: Dict[str, Any],
    violations_data: List[Dict[str, Any]]
) -> bytes:
    """
    Builds a professional, institutional-grade B2B compliance audit report PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom restrained palette styles matching Linear/Stripe ops aesthetic
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=14
    )
    section_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=14,
        spaceAfter=8
    )
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#334155')
    )
    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0f172a')
    )
    cell_header = ParagraphStyle(
        'CellHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#ffffff')
    )

    story = []

    # Header Bar
    story.append(Paragraph("APEX COMPLIANCE AUDIT REPORT", title_style))
    story.append(Paragraph(
        f"Tenant: <b>{tenant_name}</b> &nbsp;|&nbsp; Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} &nbsp;|&nbsp; Framework: BSA / AML / OFAC V1",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=0, spaceAfter=14))

    # Executive KPI Summary Table
    story.append(Paragraph("EXECUTIVE SUMMARY & KEY METRICS", section_heading))
    
    score = summary_data.get("compliance_score", 100.0)
    total_records = summary_data.get("total_records", 0)
    total_violations = summary_data.get("total_violations", 0)
    critical_count = sum(1 for v in violations_data if v.get("severity") == "CRITICAL")
    high_count = sum(1 for v in violations_data if v.get("severity") == "HIGH")
    open_count = summary_data.get("open_violations", 0)

    summary_table_data = [
        [
            Paragraph("<b>Compliance Score</b>", cell_style),
            Paragraph(f"<b>{score:.1f}%</b>", cell_bold),
            Paragraph("<b>Total Audited Records</b>", cell_style),
            Paragraph(f"<b>{total_records:,}</b>", cell_bold)
        ],
        [
            Paragraph("<b>Total Flagged Violations</b>", cell_style),
            Paragraph(f"<b>{total_violations:,}</b>", cell_bold),
            Paragraph("<b>Critical Severity Findings</b>", cell_style),
            Paragraph(f"<font color='#dc2626'><b>{critical_count:,}</b></font>", cell_bold)
        ],
        [
            Paragraph("<b>High Severity Findings</b>", cell_style),
            Paragraph(f"<b>{high_count:,}</b>", cell_bold),
            Paragraph("<b>Pending / Open Status</b>", cell_style),
            Paragraph(f"<b>{open_count:,}</b>", cell_bold)
        ]
    ]

    summary_table = Table(summary_table_data, colWidths=[1.8 * inch, 1.2 * inch, 2.0 * inch, 1.5 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # Detailed Violations Ledger
    story.append(Paragraph(f"DETAILED VIOLATION FINDINGS ({len(violations_data)} Records)", section_heading))

    table_rows = [
        [
            Paragraph("TXN ID", cell_header),
            Paragraph("Rule Reference", cell_header),
            Paragraph("Severity", cell_header),
            Paragraph("Status", cell_header),
            Paragraph("Violation Finding / Audit Message", cell_header),
        ]
    ]

    # Limit to top 50 in PDF to prevent unbounded document sizes
    for v in violations_data[:50]:
        sev = v.get("severity", "MEDIUM")
        sev_color = "#dc2626" if sev == "CRITICAL" else ("#ea580c" if sev == "HIGH" else "#ca8a04")
        
        table_rows.append([
            Paragraph(v.get("transaction_id", "N/A"), cell_bold),
            Paragraph(f"{v.get('rule_code', '')}<br/>{v.get('rule_name', '')[:25]}", cell_style),
            Paragraph(f"<font color='{sev_color}'><b>{sev}</b></font>", cell_style),
            Paragraph(v.get("status", "OPEN"), cell_style),
            Paragraph(v.get("message", "")[:120], cell_style)
        ])

    violations_table = Table(table_rows, colWidths=[1.0 * inch, 1.7 * inch, 0.8 * inch, 0.9 * inch, 3.1 * inch])
    violations_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('TOPPADDING', (0, 0), (-1, 0), 5),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f1f5f9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(violations_table)
    story.append(Spacer(1, 18))

    # Auditor Attestation Block
    attestation = KeepTogether([
        Paragraph("AUDITOR ATTESTATION & COMPLIANCE SIGN-OFF", section_heading),
        Paragraph(
            "This report was programmatically generated based on deterministic rule evaluation across ingested transaction records. "
            "All Critical and High violations require operational review, justification, and resolution tracking in the audit logs prior to regulatory filing.",
            cell_style
        ),
        Spacer(1, 16),
        Table([
            [
                Paragraph("<b>Audited By:</b> ___________________________", cell_style),
                Paragraph("<b>Compliance Officer Signature:</b> ___________________________", cell_style),
                Paragraph("<b>Date:</b> ______________", cell_style)
            ]
        ], colWidths=[2.5 * inch, 3.5 * inch, 1.5 * inch])
    ])
    story.append(attestation)

    doc.build(story)
    return buffer.getvalue()
