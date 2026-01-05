from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.units import inch
from django.http import HttpResponse
from io import BytesIO
import os

def generate_scan_pdf(scan):
    """
    Generates a professional, interactive PDF using ReportLab Platypus.
    """
    # 1. Setup the response and buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40,
        title=f"Scan Report {scan.id}"
    )

    # 2. Prepare Styles
    styles = getSampleStyleSheet()
    
    # Custom Header Style
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#2C3E50"),
        spaceAfter=20
    )
    
    # Custom Body Style
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=16
    )

    # Elements list to hold the flowables
    elements = []

    # --- SECTION 1: HEADER & WATERMARK EFFECT ---
    # Note: Platypus handles flow, but we can add a logo/title
    elements.append(Paragraph("DERMACARE AI", title_style))
    elements.append(Paragraph("<b>Skin Diagnosis Report</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Report ID: #{scan.id} | Date: 2024-05-20", styles['Normal'])) # Replace date with scan.created_at
    elements.append(Spacer(1, 20))

    # --- SECTION 2: DIAGNOSIS & IMAGE GRID ---
    
    # Determine Color for Severity
    severity_color = colors.green if scan.is_safe else colors.red
    
    # Left Column: Text Data
    diagnosis_data = [
        [Paragraph("<b>Diagnosis:</b>", body_style), Paragraph(str(scan.diagnosis), body_style)],
        [Paragraph("<b>Confidence:</b>", body_style), f"{scan.confidence}%"],
        [Paragraph("<b>Severity:</b>", body_style), Paragraph(f'<font color="{severity_color}">{scan.severity}</font>', body_style)],
        [Paragraph("<b>Status:</b>", body_style), Paragraph(f"<b>{'SAFE' if scan.is_safe else 'ATTENTION REQUIRED'}</b>", body_style)],
    ]

    # Right Column: Image Processing
    scan_img = None
    if scan.image and hasattr(scan.image, 'path') and os.path.exists(scan.image.path):
        try:
            # Constrain image to 2 inches width, maintain aspect ratio
            scan_img = Image(scan.image.path, width=2*inch, height=2*inch)
            scan_img.hAlign = 'CENTER'
        except Exception:
            scan_img = Paragraph("[Image Error]", body_style)
    else:
        scan_img = Paragraph("[No Image Available]", body_style)

    # Combine into a Master Table (2 Columns)
    # Col 1: Diagnosis Table, Col 2: The Image
    
    # Create an inner table for the text stats to format them nicely
    text_table = Table(diagnosis_data, colWidths=[80, 150])
    text_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TEXTCOLOR', (0,0), (0,-1), colors.grey),
    ]))

    main_table_data = [[text_table, scan_img]]
    main_table = Table(main_table_data, colWidths=[250, 200])
    main_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'CENTER'), # Center image
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.lightgrey), # Divider line
        ('BOTTOMPADDING', (0,0), (-1,-1), 20),
    ]))
    
    elements.append(main_table)
    elements.append(Spacer(1, 20))

    # --- SECTION 3: MEDICAL ADVICE (Text Wrapping) ---
    elements.append(Paragraph("Medical Advice & Analysis", styles['Heading3']))
    
    # Paragraph handles newline splitting and wrapping automatically
    # We replace pure newlines with <br/> for HTML-like rendering in ReportLab
    formatted_advice = scan.advice.replace('\n', '<br/>')
    elements.append(Paragraph(formatted_advice, body_style))
    elements.append(Spacer(1, 30))

    # --- SECTION 4: INTERACTIVE ELEMENTS (Links & QR) ---
    
    # A. Clickable Hyperlinks
    link_style = ParagraphStyle(
        'LinkStyle',
        parent=body_style,
        textColor=colors.blue,
        underline=True
    )
    
    # Hypothetical URLs based on ID
    booking_url = f"https://dermacare-ai.com/book/{scan.id}"
    details_url = f"https://dermacare-ai.com/report/{scan.id}"

    action_text = f"""
    <b>Recommended Actions:</b><br/>
    1. <a href="{details_url}" color="blue">View Full Interactive Report Online</a><br/>
    2. <a href="{booking_url}" color="blue">Book Follow-up Appointment with Dr. Smith</a>
    """
    elements.append(Paragraph(action_text, body_style))
    elements.append(Spacer(1, 20))

    # B. QR Code Generation
    # We generate a QR code that points to the details URL
    qr_code = qr.QrCodeWidget(details_url)
    qr_code.barWidth = 35
    qr_code.barHeight = 35
    
    # Drawing wrapper for the QR code
    d = Drawing(100, 100)
    d.add(qr_code)
    
    # Signature Block + QR Code Side-by-Side
    signature_text = """
    <b>Dr. John Smith, MD</b><br/>
    Board Certified Dermatologist<br/>
    <i>Dermacare AI Analysis</i>
    """
    
    footer_data = [[Paragraph(signature_text, body_style), d]]
    footer_table = Table(footer_data, colWidths=[350, 100])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    
    elements.append(footer_table)

    # 3. Build the PDF
    doc.build(elements)

    # 4. Return HTTP Response
    pdf_data = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="scan_report_{scan.id}.pdf"'
    response.write(pdf_data)
    
    return response