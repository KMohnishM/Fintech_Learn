import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_styled_pdf(filename, title, content_elements):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0D3B66"),
        spaceAfter=10
    )

    story = [
        Paragraph(title, header_style),
        Spacer(1, 10)
    ]
    story.extend(content_elements)
    doc.build(story)
    print(f"Generated: {filename}")

def build_benchmark_suite():
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontName='Helvetica-Bold')

    base_dir = os.path.join(os.path.dirname(__file__), "..", "resources", "test-documents")

    # ==============================================================
    # 1. CASE 1: CLEAN COMPLIANT PRESENTATION
    # ==============================================================
    case1_dir = os.path.join(base_dir, "case1_clean")

    # Bill of Lading
    bl_data = [
        ["CARRIER / SHIPPING LINE:", "MAERSK LINE A/S"],
        ["B/L NUMBER:", "MSK-IN-BOM-2026-9901"],
        ["VESSEL / VOYAGE:", "MAERSK KARACHI / VOY 2604N"],
        ["PORT OF LOADING:", "PORT OF NHAVA SHEVA, INDIA"],
        ["PORT OF DISCHARGE:", "PORT OF YOKOHAMA, JAPAN"],
        ["SHIPPED ON BOARD DATE:", "15-NOV-2026"],
        ["NOTATION:", "CLEAN ON BOARD"],
        ["TOTAL PACKAGES:", "50 CRATES"],
        ["GROSS WEIGHT:", "4,200.0 KG"],
        ["GOODS DESCRIPTION:", "10,000 UNITS OF AUTOMOTIVE MICROCONTROLLERS (MODEL MCU-900). CIF YOKOHAMA."]
    ]
    t1 = Table(bl_data, colWidths=[200, 320])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F0F4F8")),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    create_styled_pdf(
        os.path.join(case1_dir, "bill_of_lading.pdf"),
        "OCEAN BILL OF LADING (NEGOTIABLE)",
        [t1]
    )

    # Commercial Invoice
    inv_data = [
        ["SELLER / EXPORTER:", "TATA ELECTRONICS PRIVATE LIMITED, BANGALORE, INDIA"],
        ["BUYER / APPLICANT:", "TOYOTA TSUSHO CORPORATION, NAGOYA, JAPAN"],
        ["INVOICE NUMBER:", "INV-TATA-2026-8801"],
        ["INVOICE DATE:", "12-NOV-2026"],
        ["LC REFERENCE:", "GB-LC-2026-8891"],
        ["TERMS OF DELIVERY:", "CIF YOKOHAMA (INCOTERMS 2020)"],
        ["DESCRIPTION OF GOODS:", "10,000 UNITS OF AUTOMOTIVE MICROCONTROLLERS (MODEL MCU-900). UNIT PRICE USD 25.00 CIF YOKOHAMA. PACKED IN 50 CRATES."],
        ["TOTAL AMOUNT:", "USD 250,000.00"]
    ]
    t2 = Table(inv_data, colWidths=[200, 320])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F0F4F8")),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    create_styled_pdf(
        os.path.join(case1_dir, "commercial_invoice.pdf"),
        "COMMERCIAL INVOICE",
        [t2]
    )

    # Packing List
    pl_data = [
        ["PACKING LIST NUMBER:", "PL-TATA-2026-8801"],
        ["NUMBER OF PACKAGES:", "50 CRATES"],
        ["NET WEIGHT:", "3,900.0 KG"],
        ["GROSS WEIGHT:", "4,200.0 KG"],
        ["MEASUREMENT:", "18.5 CBM"],
        ["CONTAINER NUMBER:", "MSKU-781920-4"]
    ]
    t3 = Table(pl_data, colWidths=[200, 320])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F0F4F8")),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    create_styled_pdf(
        os.path.join(case1_dir, "packing_list.pdf"),
        "DETAILED PACKING LIST",
        [t3]
    )

    # Insurance Certificate (110% of $250,000 = $275,000)
    ins_data = [
        ["INSURER:", "NEW INDIA ASSURANCE CO. LTD."],
        ["CERTIFICATE NUMBER:", "INS-POL-2026-4401"],
        ["INSURED AMOUNT:", "USD 275,000.00"],
        ["COVERAGE BASIS:", "110% OF CIF INVOICE VALUE AGAINST ALL RISKS (INSTITUTE CARGO CLAUSES A)"],
        ["VOYAGE:", "FROM NHAVA SHEVA TO YOKOHAMA"]
    ]
    t4 = Table(ins_data, colWidths=[200, 320])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F0F4F8")),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    create_styled_pdf(
        os.path.join(case1_dir, "insurance_certificate.pdf"),
        "MARINE CARGO INSURANCE CERTIFICATE",
        [t4]
    )

    # ==============================================================
    # 2. CASE 2: LATE SHIPMENT DISCREPANCY (UCP 600 Art. 20)
    # ==============================================================
    case2_dir = os.path.join(base_dir, "case2_late_shipment")
    bl_late = [
        ["CARRIER / SHIPPING LINE:", "MAERSK LINE A/S"],
        ["B/L NUMBER:", "MSK-IN-BOM-2026-9902"],
        ["VESSEL / VOYAGE:", "MAERSK KARACHI / VOY 2606N"],
        ["PORT OF LOADING:", "PORT OF NHAVA SHEVA, INDIA"],
        ["PORT OF DISCHARGE:", "PORT OF YOKOHAMA, JAPAN"],
        ["SHIPPED ON BOARD DATE:", "05-DEC-2026"],  # LC requires on/before 30-NOV-2026!
        ["NOTATION:", "CLEAN ON BOARD"],
        ["GROSS WEIGHT:", "4,200.0 KG"]
    ]
    t_late = Table(bl_late, colWidths=[200, 320])
    t_late.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#FEE2E2")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#EF4444")),
    ]))
    create_styled_pdf(
        os.path.join(case2_dir, "bill_of_lading.pdf"),
        "OCEAN BILL OF LADING (LATE SHIPMENT DISCREPANT)",
        [t_late]
    )

    # ==============================================================
    # 3. CASE 3: INVOICE DESCRIPTION MISMATCH (UCP 600 Art. 18)
    # ==============================================================
    case3_dir = os.path.join(base_dir, "case3_description_mismatch")
    inv_mismatch = [
        ["INVOICE NUMBER:", "INV-TATA-2026-8803"],
        ["DESCRIPTION OF GOODS:", "10,000 UNITS OF ELECTRONIC COMPONENTS."], # Omitted MODEL MCU-900!
        ["TOTAL AMOUNT:", "USD 250,000.00"]
    ]
    t_mismatch = Table(inv_mismatch, colWidths=[200, 320])
    t_mismatch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#FEE2E2")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#EF4444")),
    ]))
    create_styled_pdf(
        os.path.join(case3_dir, "commercial_invoice.pdf"),
        "COMMERCIAL INVOICE (DESCRIPTION MISMATCH)",
        [t_mismatch]
    )

    # ==============================================================
    # 4. CASE 4: WEIGHT CONFLICT ACROSS DOCUMENTS (UCP 600 Art. 14)
    # ==============================================================
    case4_dir = os.path.join(base_dir, "case4_weight_conflict")
    pl_weight = [
        ["PACKING LIST NUMBER:", "PL-TATA-2026-8804"],
        ["GROSS WEIGHT:", "4,800.0 KG"], # Conflicts with B/L 4,200 KG!
        ["TOTAL PACKAGES:", "50 CRATES"]
    ]
    t_weight = Table(pl_weight, colWidths=[200, 320])
    t_weight.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#FEE2E2")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#EF4444")),
    ]))
    create_styled_pdf(
        os.path.join(case4_dir, "packing_list.pdf"),
        "PACKING LIST (WEIGHT CONFLICT)",
        [t_weight]
    )

    # ==============================================================
    # 5. CASE 5: UNDER-INSURANCE DISCREPANCY (UCP 600 Art. 28)
    # ==============================================================
    case5_dir = os.path.join(base_dir, "case5_under_insurance")
    ins_under = [
        ["CERTIFICATE NUMBER:", "INS-POL-2026-4405"],
        ["INSURED AMOUNT:", "USD 250,000.00"], # Only 100%, missing mandatory 110% = $275,000!
        ["COVERAGE BASIS:", "100% OF INVOICE VALUE"]
    ]
    t_ins = Table(ins_under, colWidths=[200, 320])
    t_ins.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#FEE2E2")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#EF4444")),
    ]))
    create_styled_pdf(
        os.path.join(case5_dir, "insurance_certificate.pdf"),
        "INSURANCE CERTIFICATE (UNDER-INSURED)",
        [t_ins]
    )

    print("\n[SUCCESS] All 5 benchmark test scenarios generated successfully in resources/test-documents/")

if __name__ == "__main__":
    build_benchmark_suite()
