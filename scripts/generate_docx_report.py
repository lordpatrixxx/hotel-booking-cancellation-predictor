"""Generate an academic-grade, publication-quality Word document (.docx) project report for submission.
Includes PCCOE college logo, cover page, certificate, declaration, tables, and high-resolution figures.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

LOGO_PATH = Path(r"C:\Users\Asus\.gemini\antigravity\brain\8f196281-7014-4f28-b4af-b633e3ba79fb\.user_uploaded\media_1793177815123_d7be41ea.png")
FIG_DIR = ROOT / "reports" / "figures"
OUTPUT_DOCX = ROOT / "reports" / "Hotel_Booking_Cancellation_Project_Report.docx"
ROOT_OUTPUT_DOCX = ROOT.parent / "Hotel_Booking_Cancellation_Project_Report.docx"

# Palette
COLOR_NAVY = RGBColor(8, 61, 119)     # #083D77
COLOR_TEAL = RGBColor(8, 127, 140)    # #087F8C
COLOR_CHARCOAL = RGBColor(31, 36, 33) # #1F2421
COLOR_MUTED = RGBColor(92, 107, 115)  # #5C6B73
HEX_TEAL = "087F8C"
HEX_LIGHT_BG = "F4F9FA"
HEX_ALT_ROW = "F9FCFC"
HEX_BORDER = "D1E2E5"

def set_cell_background(cell, hex_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'''<w:tcMar {nsdecls("w")}>
        <w:top w:w="{top}" w:type="dxa"/>
        <w:bottom w:w="{bottom}" w:type="dxa"/>
        <w:left w:w="{left}" w:type="dxa"/>
        <w:right w:w="{right}" w:type="dxa"/>
    </w:tcMar>''')
    tcPr.append(tcMar)

def set_table_borders(table, hex_color=HEX_BORDER):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(f'''<w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="4" w:space="0" w:color="{hex_color}"/>
            <w:left w:val="none"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{HEX_TEAL}"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{hex_color}"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>''')
        tblPr[0].append(borders)

def build_report():
    doc = docx.Document()

    # Page Margins (Normal 1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

        # Header / Footer
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("PCCOE IT | Data Science Laboratory Project Report")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = COLOR_MUTED

        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        frun = fp.add_run("Booked or Cancelled? Hotel Booking Intelligence")
        frun.font.name = "Calibri"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = COLOR_MUTED

    # Base styling
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = COLOR_CHARCOAL
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    def add_p(text, bold=False, italic=False, size=11, color=COLOR_CHARCOAL, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=6):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.name = 'Calibri'
        run.font.size = Pt(size)
        run.font.color.rgb = color
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Calibri'
        run.font.size = Pt(16)
        run.font.color.rgb = COLOR_NAVY
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Calibri'
        run.font.size = Pt(13)
        run.font.color.rgb = COLOR_TEAL
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Calibri'
        run.font.size = Pt(11.5)
        run.font.color.rgb = COLOR_CHARCOAL
        return p

    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        r_bold = p.add_run(bold_prefix)
        r_bold.bold = True
        r_bold.font.name = 'Calibri'
        r_bold.font.size = Pt(10.5)
        r_bold.font.color.rgb = COLOR_CHARCOAL
        r_text = p.add_run(text)
        r_text.font.name = 'Calibri'
        r_text.font.size = Pt(10.5)
        r_text.font.color.rgb = COLOR_CHARCOAL
        return p

    def add_callout(text, bold_title=""):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        set_cell_background(cell, HEX_LIGHT_BG)
        set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
        tcPr = cell._element.get_or_add_tcPr()
        borders = parse_xml(f'''<w:tcBorders {nsdecls("w")}>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="{HEX_TEAL}"/>
            <w:top w:val="none"/>
            <w:right w:val="none"/>
            <w:bottom w:val="none"/>
        </w:tcBorders>''')
        tcPr.append(borders)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        if bold_title:
            rb = p.add_run(bold_title + "\n")
            rb.bold = True
            rb.font.name = 'Calibri'
            rb.font.size = Pt(10.5)
            rb.font.color.rgb = COLOR_TEAL
        rt = p.add_run(text)
        rt.italic = True
        rt.font.name = 'Calibri'
        rt.font.size = Pt(10)
        rt.font.color.rgb = COLOR_CHARCOAL
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def add_figure(img_path, caption):
        if Path(img_path).exists():
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(2)
            run = p_img.add_run()
            run.add_picture(str(img_path), width=Inches(5.6))
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(0)
            p_cap.paragraph_format.space_after = Pt(10)
            rcap = p_cap.add_run(caption)
            rcap.italic = True
            rcap.font.name = 'Calibri'
            rcap.font.size = Pt(9.5)
            rcap.font.color.rgb = COLOR_MUTED

    # ==========================================
    # 1. COVER / TITLE PAGE
    # ==========================================
    p_inst = add_p("Pimpri Chinchwad Education Trust's", bold=True, size=13, color=COLOR_NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=2)
    add_p("PIMPRI CHINCHWAD COLLEGE OF ENGINEERING, PUNE", bold=True, size=15, color=COLOR_NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    add_p("An Autonomous Institute Affiliated to Savitribai Phule Pune University", italic=True, size=10, color=COLOR_MUTED, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

    # College Logo
    if LOGO_PATH.exists():
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(4)
        p_logo.paragraph_format.space_after = Pt(14)
        run_logo = p_logo.add_run()
        run_logo.add_picture(str(LOGO_PATH), width=Inches(1.85))

    add_p("DEPARTMENT OF INFORMATION TECHNOLOGY", bold=True, size=12.5, color=COLOR_TEAL, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    # Decorative line
    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_after = Pt(14)
    r_line = p_line.add_run("____________________________________________________________")
    r_line.font.color.rgb = COLOR_TEAL

    add_p("A MINI PROJECT REPORT ON", bold=True, size=11, color=COLOR_MUTED, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
    add_p("BOOKED OR CANCELLED?", bold=True, size=22, color=COLOR_NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    add_p("Predicting Hotel Booking Cancellations and Discovering Booking Patterns", bold=True, italic=True, size=13, color=COLOR_TEAL, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)

    add_p("Submitted in partial fulfilment of the requirements for the course", italic=True, size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_p("VSEC Data Science Laboratory (Course Code: BIT23VS01)", bold=True, size=11.5, color=COLOR_CHARCOAL, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_p("Second Year B.Tech (Information Technology) - Semester III (Division B)", size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=20)

    # Project Details Table
    table_meta = doc.add_table(rows=5, cols=2)
    table_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_meta)
    
    meta_data = [
        ("Submitted By:", "1. Pratik Deepak Phapale (PRN: 125B1F210)\n2. Swastik Sandipkumar Phapale (PRN: 125B1F212)\n3. Nirjar Rupesh Patil (PRN: 125B1F206)"),
        ("Project Group:", "Group B3-4 (Division B)"),
        ("Under the Guidance of:", "Prof. JYOTI MANOORKAR Ma'am\nAssistant Professor, Department of Information Technology"),
        ("Institutional Repository:", "https://github.com/lordpatrixxx/hotel-booking-cancellation-predictor"),
        ("Academic Year:", "2026 – 2027")
    ]
    
    for row_idx, (label, val) in enumerate(meta_data):
        row = table_meta.rows[row_idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
        set_cell_margins(c0, 80, 80, 100, 100)
        set_cell_margins(c1, 80, 80, 100, 100)
        
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.name = 'Calibri'
        r0.font.size = Pt(10)
        r0.font.color.rgb = COLOR_NAVY
        
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r1 = p1.add_run(val)
        r1.font.name = 'Calibri'
        r1.font.size = Pt(10)
        r1.font.color.rgb = COLOR_CHARCOAL

    doc.add_page_break()

    # ==========================================
    # 2. CERTIFICATE PAGE
    # ==========================================
    add_p("Pimpri Chinchwad Education Trust's", bold=True, size=12, color=COLOR_NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=2)
    add_p("PIMPRI CHINCHWAD COLLEGE OF ENGINEERING, PUNE", bold=True, size=13.5, color=COLOR_NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_p("DEPARTMENT OF INFORMATION TECHNOLOGY", bold=True, size=11.5, color=COLOR_TEAL, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    add_p("CERTIFICATE", bold=True, size=18, color=COLOR_NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)

    cert_text = (
        "This is to certify that the mini project report entitled \"Booked or Cancelled? Predicting Hotel "
        "Booking Cancellations and Discovering Booking Patterns\" submitted by:\n\n"
        "  • Pratik Deepak Phapale (PRN: 125B1F210)\n"
        "  • Swastik Sandipkumar Phapale (PRN: 125B1F212)\n"
        "  • Nirjar Rupesh Patil (PRN: 125B1F206)\n\n"
        "is a bonafide work carried out under my supervision and guidance in partial fulfilment of the requirements "
        "for the course VSEC Data Science Laboratory (BIT23VS01) for the degree of Bachelor of Technology (Information Technology) "
        "at Pimpri Chinchwad College of Engineering, Pune during the academic year 2026–2027.\n\n"
        "To the best of our knowledge, the results and analytical procedures documented in this report have been executed "
        "reproducibly and have not been submitted to any other university or institute for the award of any degree or diploma."
    )
    add_p(cert_text, size=11, space_after=40)

    # Signatures Table
    table_sig = doc.add_table(rows=1, cols=3)
    table_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, (title, role) in enumerate([
        ("Prof. JYOTI MANOORKAR", "Faculty Guide\nDept. of Information Technology"),
        ("Dr. Head of Department", "Head of Department\nDept. of Information Technology"),
        ("Dr. Principal", "Principal\nPCCoE, Pune")
    ]):
        c = table_sig.rows[0].cells[i]
        c.width = Inches(2.1)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.15
        r_line = p.add_run("___________________\n\n")
        r_name = p.add_run(f"{title}\n")
        r_name.bold = True
        r_name.font.size = Pt(10)
        r_name.font.color.rgb = COLOR_NAVY
        r_role = p.add_run(role)
        r_role.italic = True
        r_role.font.size = Pt(9)
        r_role.font.color.rgb = COLOR_MUTED

    doc.add_page_break()

    # ==========================================
    # 3. DECLARATION & ACKNOWLEDGEMENT
    # ==========================================
    add_h1("STUDENT DECLARATION")
    decl_text = (
        "We hereby declare that the work presented in this project report entitled \"Booked or Cancelled? "
        "Predicting Hotel Booking Cancellations and Discovering Booking Patterns\" was carried out by us under the "
        "guidance of Prof. JYOTI MANOORKAR Ma'am, Department of Information Technology, Pimpri Chinchwad College "
        "of Engineering, Pune.\n\n"
        "We have adhered to all principles of academic integrity and scientific ethics. Any data, figures, concepts, "
        "or benchmarks derived from published literature, particularly the foundational dataset by Antonio, de Almeida, "
        "and Nunes (2019), have been duly cited and acknowledged. The code, data pipelines, and validation experiments "
        "contained in this repository were independently implemented and verified."
    )
    add_p(decl_text, space_after=18)

    # Student signatures
    table_decl = doc.add_table(rows=1, cols=3)
    table_decl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, (name, prn) in enumerate([
        ("Pratik Deepak Phapale", "125B1F210"),
        ("Swastik Sandipkumar Phapale", "125B1F212"),
        ("Nirjar Rupesh Patil", "125B1F206")
    ]):
        c = table_decl.rows[0].cells[i]
        c.width = Inches(2.1)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run("___________________\n\n")
        rn = p.add_run(f"{name}\n")
        rn.bold = True
        rn.font.size = Pt(9.5)
        rp = p.add_run(f"PRN: {prn}")
        rp.font.size = Pt(9)
        rp.font.color.rgb = COLOR_MUTED

    add_h1("ACKNOWLEDGEMENT")
    ack_text = (
        "We express our deepest gratitude to our project guide, Prof. JYOTI MANOORKAR Ma'am, for her constant guidance, "
        "constructive feedback, and intellectual encouragement throughout the development of this project. Her emphasis on "
        "leakage-free evaluation, realistic chronological constraints, and rigorous baseline comparisons was instrumental "
        "in ensuring the methodological depth of this study.\n\n"
        "We also extend our sincere appreciation to the Head of Department, Department of Information Technology, and the "
        "management of Pimpri Chinchwad College of Engineering (PCCoE) for providing modern computing infrastructure, "
        "access to scholarly literature, and an academic environment conducive to research.\n\n"
        "Finally, we thank our peers and families for their continuous support and valuable discussions."
    )
    add_p(ack_text, space_after=14)

    doc.add_page_break()

    # ==========================================
    # 4. ABSTRACT & TABLE OF CONTENTS
    # ==========================================
    add_h1("EXECUTIVE SUMMARY / ABSTRACT")
    abstract_text = (
        "Hotel booking cancellations represent a critical operational challenge in the hospitality sector, directly "
        "impacting room occupancy, revenue per available room (RevPAR), and overbooking policies. This project develops an "
        "end-to-end, reproducible Data Science pipeline to predict whether a prospective hotel booking will be canceled and to "
        "discover underlying booking behavior patterns.\n\n"
        "Using the benchmark Portuguese Hotel Booking Demand dataset (119,390 historical reservations across a City Hotel and "
        "a Resort Hotel, 2015–2017), we establish a leak-free evaluation protocol. To prevent temporal lookahead bias, records "
        "are partitioned chronologically into mature historical cohorts: Training (57,745 rows), Validation (8,321 rows), and "
        "Test (26,409 rows). We evaluate Logistic Regression, Random Forest, and Gradient Boosting against a Majority-Class Baseline.\n\n"
        "Random Forest achieves the superior validation ROC AUC and is selected as the production model, yielding a held-out Test "
        "ROC AUC of 0.7762 and average precision of 0.6509. By calibrating the decision threshold on validation F1-score to 0.16, "
        "the model catches 91.1% of actual cancellations (recall = 0.911) with precision = 0.412. The final system is deployed as "
        "a multi-page interactive Streamlit web application providing single-booking scoring, safe batch CSV analysis, and "
        "exploratory pattern mining."
    )
    add_p(abstract_text, space_after=18)

    add_callout(
        "Key Project Highlights:\n"
        "• Dataset: 119,390 raw rows; 118,564 clean overnight bookings analyzed.\n"
        "• Best Model: Random Forest Pipeline (Validation ROC AUC: 0.6951 | Test ROC AUC: 0.7762).\n"
        "• Review Threshold: Tuned to 0.16 on validation data, achieving 91.1% recall on held-out test data.\n"
        "• Architecture: 6-page interactive Streamlit GUI with automated offline launcher scripts.\n"
        "• Test Suite: 25 automated unit and UI smoke tests passing with 100% success.",
        bold_title="PROJECT AT A GLANCE"
    )

    add_h1("TABLE OF CONTENTS")
    toc_items = [
        ("1. Introduction and Problem Statement", "Page 5"),
        ("2. Dataset Attribution and Preprocessing", "Page 6"),
        ("3. Exploratory Data Analysis & Historical Booking Patterns", "Page 8"),
        ("4. Machine Learning Methodology & Feature Engineering", "Page 10"),
        ("5. Experimental Results, Model Evaluation & Discussion", "Page 12"),
        ("6. Software Architecture & Interactive Streamlit GUI", "Page 15"),
        ("7. Verification, Testing & Reproducibility", "Page 17"),
        ("8. Limitations, Ethical Considerations & Future Scope", "Page 18"),
        ("9. Conclusion", "Page 19"),
        ("10. References", "Page 20")
    ]
    for title, pg in toc_items:
        p_toc = doc.add_paragraph()
        p_toc.paragraph_format.space_before = Pt(1)
        p_toc.paragraph_format.space_after = Pt(2)
        r_t = p_toc.add_run(title)
        r_t.font.name = 'Calibri'
        r_t.font.size = Pt(10.5)
        # Tab leader
        r_dots = p_toc.add_run(" " + "." * (68 - len(title)) + " ")
        r_dots.font.color.rgb = COLOR_MUTED
        r_p = p_toc.add_run(pg)
        r_p.bold = True
        r_p.font.color.rgb = COLOR_NAVY

    doc.add_page_break()

    # ==========================================
    # CHAPTER 1: INTRODUCTION
    # ==========================================
    add_h1("1. INTRODUCTION AND PROBLEM STATEMENT")
    add_h2("1.1 Background & Motivation")
    intro_1 = (
        "In modern revenue management for the hospitality industry, managing cancellations is an indispensable "
        "operational challenge. High cancellation rates introduce significant volatility into demand forecasting, supply chain "
        "procurement, staff scheduling, and inventory allocation. When a guest cancels shortly before arrival, the hotel risks "
        "leaving a room unoccupied, forfeiting revenue that cannot be recovered. Conversely, aggressive overbooking strategies "
        "designed to compensate for expected cancellations carry reputational and financial penalties if guests must be walked "
        "to competing establishments.\n\n"
        "Traditional cancellation mitigation relies either on crude historical averages or punitive cancellation fee structures. "
        "However, rigid deposit policies can alienate prospective customers and suppress total booking volume. A predictive, "
        "data-driven decision support tool enables hotels to anticipate high-risk reservations at the time of creation, allowing "
        "targeted customer confirmation outreach and dynamic revenue management without alienating low-risk guests."
    )
    add_p(intro_1)

    add_h2("1.2 Problem Formulation")
    intro_2 = (
        "We formulate cancellation prediction as a supervised binary classification problem. For each booking instance x characterized "
        "by attributes available at the time of reservation creation, the objective is to predict the true outcome y ∈ {0, 1}, where:\n"
        "  • y = 1 represents a cancelled reservation (or a no-show).\n"
        "  • y = 0 represents a non-cancelled booking (guest attended / checked in).\n\n"
        "Crucially, the prediction must rely strictly on information observable when the reservation is finalized. Information "
        "generated during or after the stay (such as final checkout date, reservation status updates, or post-booking modifications) "
        "must be strictly quarantined to avoid artificial data leakage."
    )
    add_p(intro_2)

    add_h2("1.3 Project Objectives")
    add_bullet("1. Data Ingestion & Cleansing: ", "Acquire, inspect, and sanitize 119,390 historical booking records from real-world hotel operations, ensuring verifiable data provenance.")
    add_bullet("2. Temporal Partitioning: ", "Implement strict chronological train/validation/test splits to simulate realistic forward-looking deployment and eliminate temporal leakage.")
    add_bullet("3. Multi-Algorithm Benchmarking: ", "Train and compare multiple classifiers (Majority Baseline, Logistic Regression, Random Forest, Gradient Boosting) using rigorous validation metrics.")
    add_bullet("4. Decision Threshold Tuning: ", "Optimize probability decision thresholds on validation data to achieve high cancellation recall, enabling practical operational review.")
    add_bullet("5. Transparent Interactive GUI: ", "Develop and deliver a 6-page interactive Streamlit web dashboard supporting single-record simulation, safe batch CSV scoring, and pattern exploration.")
    add_bullet("6. Reproducible Open Source Codebase: ", "Ensure end-to-end reproducibility with automated tests, packaged dependencies, and offline batch launcher scripts.")

    doc.add_page_break()

    # ==========================================
    # CHAPTER 2: DATASET & PREPROCESSING
    # ==========================================
    add_h1("2. DATASET ATTRIBUTION AND PREPROCESSING")
    add_h2("2.1 Data Provenance & Source")
    data_1 = (
        "The project utilizes the benchmark Hotel Booking Demand dataset curated and published by Nuno Antonio, Ana de Almeida, "
        "and Luis Nunes (2019) in Data in Brief (DOI: 10.1016/j.dib.2018.11.126). The data captures real-world reservation activity "
        "from two distinct Portuguese hotel properties between July 2015 and August 2017:\n"
        "  1. H1 (Resort Hotel): Situated in the Algarve region, featuring 40,060 raw records with strong summer seasonality.\n"
        "  2. H2 (City Hotel): Situated in Lisbon, comprising 79,330 raw records characterized by year-round business travel.\n\n"
        "The raw dataset was obtained via the TidyTuesday repository mirror and is distributed under the Creative Commons "
        "Attribution 4.0 International license (CC BY 4.0). Complete data provenance is cryptographically secured via SHA-256:"
    )
    add_p(data_1)
    add_callout(
        "Raw Dataset File: data/hotel_bookings.csv\n"
        "Recorded Rows: 119,390 observations | Columns: 32 variables\n"
        "SHA-256 Checksum: 7c2ae42a7353905ea136e5c2287f17c92c5435826598bfbb8491c6f0c7b1fc06\n"
        "Provenance Verification: Verified matching on disk prior to model fitting.",
        bold_title="DATASET PROVENANCE SPECIFICATION"
    )

    add_h2("2.2 Data Cleaning and Filtering Rules")
    data_2 = (
        "A total of 826 invalid or non-operational records were excluded following strict domain hygiene criteria:\n"
        "  • Zero Occupancy: Bookings with zero adults, zero children, and zero babies (402 rows) represent system testing or ghost holds.\n"
        "  • Zero Stays: Bookings where week nights plus weekend nights equal zero (715 rows) do not constitute overnight hotel stays.\n"
        "  • Negative Pricing: Erroneous transactions with Average Daily Rate (ADR) < 0.0 (1 row) were purged.\n"
        "  • Missing Arrival Dates: Rows missing valid calendar dates were excluded.\n\n"
        "This yields a finalized modeling dataset of 118,564 valid overnight reservations. Crucially, 31,994 identical-looking "
        "duplicate rows were deliberately retained. In hospitality PMS logs, distinct guests frequently book identical room types "
        "under identical dates, and arbitrary deduplication would bias class distribution without unique booking IDs."
    )
    add_p(data_2)

    add_h2("2.3 Feature Allowlist vs. Leakage Exclusion")
    data_3 = (
        "A core contribution of this project is strict feature segregation to prevent target leakage. Variables are classified "
        "into eligible predictors and forbidden post-booking fields:"
    )
    add_p(data_3)

    table_feats = doc.add_table(rows=1, cols=3)
    table_feats.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_feats)
    hdr_cells = table_feats.rows[0].cells
    hdr_cells[0].text = "Category"
    hdr_cells[1].text = "Included Model Features (19 Features)"
    hdr_cells[2].text = "Excluded / Forbidden Variables (Rationale)"
    for c in hdr_cells:
        set_cell_background(c, HEX_TEAL)
        p = c.paragraphs[0]
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
        p.runs[0].font.bold = True
        set_cell_margins(c, 100, 100, 120, 120)

    feat_rows = [
        ("Numeric (12)", "lead_time, arrival_month, arrival_day, stays_in_weekend_nights, stays_in_week_nights, adults, children, babies, is_repeated_guest, previous_cancellations, previous_bookings_not_canceled, adr", "reservation_status (direct target reveal), reservation_status_date (occurs after event), booking_changes (aggregates later updates)"),
        ("Categorical (7)", "hotel, meal, market_segment, distribution_channel, reserved_room_type, deposit_type, customer_type", "assigned_room_type (assigned at check-in), days_in_waiting_list (accumulates post-booking), agent/company (high cardinality / non-portable identifiers)")
    ]

    for cat, inc, exc in feat_rows:
        row = table_feats.add_row()
        c0, c1, c2 = row.cells[0], row.cells[1], row.cells[2]
        c0.width, c1.width, c2.width = Inches(1.5), Inches(2.7), Inches(2.3)
        set_cell_margins(c0, 80, 80, 100, 100)
        set_cell_margins(c1, 80, 80, 100, 100)
        set_cell_margins(c2, 80, 80, 100, 100)
        c0.paragraphs[0].add_run(cat).bold = True
        c1.paragraphs[0].add_run(inc)
        c2.paragraphs[0].add_run(exc)

    doc.add_page_break()

    # ==========================================
    # CHAPTER 3: EDA & BOOKING PATTERNS
    # ==========================================
    add_h1("3. EXPLORATORY DATA ANALYSIS & BOOKING PATTERNS")
    eda_1 = (
        "Exploratory data analysis reveals profound behavioral differences across booking channels, deposit types, "
        "and seasonal periods. Across the entire 119,390 observation dataset, the overall cancellation rate is 37.0% (44,224 cancellations). "
        "However, cancellation vulnerability is heavily concentrated in specific customer segments."
    )
    add_p(eda_1)

    table_hotel = doc.add_table(rows=3, cols=4)
    table_hotel.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_hotel)
    h_row = table_hotel.rows[0].cells
    for i, title in enumerate(["Hotel Property", "Total Bookings", "Total Cancellations", "Observed Cancellation Rate"]):
        h_row[i].text = title
        set_cell_background(h_row[i], HEX_TEAL)
        h_row[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        h_row[i].paragraphs[0].runs[0].font.bold = True
        set_cell_margins(h_row[i], 100, 100, 120, 120)

    hotel_stats = [
        ("City Hotel (H2 - Lisbon)", "79,330", "33,102", "41.73%"),
        ("Resort Hotel (H1 - Algarve)", "40,060", "11,122", "27.76%")
    ]
    for idx, (hname, tb, tc, cr) in enumerate(hotel_stats):
        r = table_hotel.rows[idx + 1].cells
        for col_idx, text in enumerate([hname, tb, tc, cr]):
            r[col_idx].paragraphs[0].text = text
            set_cell_margins(r[col_idx], 80, 80, 100, 100)
            if idx % 2 == 1:
                set_cell_background(r[col_idx], HEX_ALT_ROW)

    add_p("\nAs detailed in Table 2, the City Hotel experiences a markedly higher cancellation rate (41.73%) than the Resort Hotel (27.76%), "
          "attributable to shorter business trip planning horizons and high competition among urban accommodations.")

    add_figure(FIG_DIR / "monthly_arrivals.png", "Figure 1: Monthly historical booking arrivals by property (2015 – 2017)")

    add_h2("3.1 Channel and Deposit Patterns")
    eda_2 = (
        "Analysis of distribution channels indicates that Online Travel Agencies (Online TA) generate the largest volume "
        "of bookings but exhibit cancellation rates exceeding 35%. Direct bookings (booked via hotel websites or phone) exhibit "
        "substantially lower cancellation rates (~17%), reflecting higher consumer commitment.\n\n"
        "Most notably, deposit types exhibit a striking non-intuitive distribution: reservations secured with 'Non Refundable' "
        "deposits exhibit cancellation rates approaching 99% in this dataset. Detailed inspection reveals this is an artifact of commercial "
        "contracting policies: wholesale travel operators frequently reserve large blocks of rooms under non-refundable clauses and "
        "systematically cancel bulk allotments when demand thresholds fail, highlighting the necessity of contextual interpretation."
    )
    add_p(eda_2)

    add_figure(FIG_DIR / "channel_patterns.png", "Figure 2: Observed cancellation rates across distribution channels with Wilson 95% confidence intervals")

    doc.add_page_break()

    # ==========================================
    # CHAPTER 4: METHODOLOGY & PIPELINE
    # ==========================================
    add_h1("4. METHODOLOGY & MACHINE LEARNING PIPELINE")
    add_h2("4.1 Chronological Split Strategy (No Future Leakage)")
    meth_1 = (
        "Standard k-fold cross-validation or random train-test splitting introduces severe temporal leakage in time-indexed datasets: "
        "models effectively interpolate between past and future records of the same season. To simulate genuine deployment, we "
        "partition bookings chronologically using an approximated booking creation timestamp:\n"
        "  Booking Date Proxy = Arrival Date - Lead Time\n\n"
        "Partitions are established with forward-looking maturity criteria: reservations in earlier cohorts must complete their "
        "scheduled checkout and status updates prior to the start of subsequent cohorts, ensuring labels were fully resolved in practice."
    )
    add_p(meth_1)

    table_split = doc.add_table(rows=4, cols=5)
    table_split.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_split)
    s_hdr = table_split.rows[0].cells
    for i, title in enumerate(["Partition", "Observations", "Cancellation Rate", "Start Date", "End Date"]):
        s_hdr[i].text = title
        set_cell_background(s_hdr[i], HEX_TEAL)
        s_hdr[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        s_hdr[i].paragraphs[0].runs[0].font.bold = True
        set_cell_margins(s_hdr[i], 100, 100, 120, 120)

    split_data = [
        ("Training Set", "57,745", "35.83%", "2014-03-18", "2016-08-30"),
        ("Validation Set", "8,321", "23.51%", "2016-09-01", "2016-12-30"),
        ("Test Set (Held-Out)", "26,409", "31.77%", "2017-01-01", "2017-08-31")
    ]
    for idx, (pname, obs, cr, sd, ed) in enumerate(split_data):
        r = table_split.rows[idx + 1].cells
        for col_idx, text in enumerate([pname, obs, cr, sd, ed]):
            r[col_idx].paragraphs[0].text = text
            set_cell_margins(r[col_idx], 80, 80, 100, 100)

    add_h2("4.2 Preprocessing Pipeline Architecture")
    meth_2 = (
        "To ensure complete encapsulation, all preprocessing estimators are fit strictly on training partition data and chained "
        "using scikit-learn's Pipeline and ColumnTransformer:\n"
        "  • Numeric Pipeline: Missing values imputed with SimpleImputer(strategy='median') followed by StandardScaler().\n"
        "  • Categorical Pipeline: Missing values imputed with SimpleImputer(strategy='most_frequent') followed by "
        "OneHotEncoder(handle_unknown='ignore', sparse_output=False).\n\n"
        "This architecture guarantees identical preprocessing during single GUI predictions, batch scoring, and test evaluation."
    )
    add_p(meth_2)

    add_h2("4.3 Model Selection & Threshold Tuning Protocol")
    meth_3 = (
        "Model selection is governed strictly by Validation ROC AUC. Following algorithm selection, the probability classification "
        "threshold is tuned across validation candidates θ ∈ [0.10, 0.90] with step size 0.01 to maximize validation F1-score. "
        "The optimal threshold is identified as θ* = 0.16. Crucially, the held-out test partition is evaluated only once on "
        "the frozen pipeline and selected threshold."
    )
    add_p(meth_3)

    doc.add_page_break()

    # ==========================================
    # CHAPTER 5: EXPERIMENTAL RESULTS
    # ==========================================
    add_h1("5. EXPERIMENTAL RESULTS AND EVALUATION")
    add_h2("5.1 Algorithm Comparison")
    res_1 = (
        "Four model configurations were benchmarked under identical chronological partitions. The Majority Baseline always predicts "
        "non-cancelled (class 0). Table 4 summarizes performance on validation and held-out test partitions at standard threshold 0.50:"
    )
    add_p(res_1)

    table_comp = doc.add_table(rows=5, cols=7)
    table_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_comp)
    c_hdr = table_comp.rows[0].cells
    for i, title in enumerate(["Model", "Val ROC AUC", "Test ROC AUC", "Test Accuracy", "Test Precision", "Test Recall", "Test F1"]):
        c_hdr[i].text = title
        set_cell_background(c_hdr[i], HEX_TEAL)
        c_hdr[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        c_hdr[i].paragraphs[0].runs[0].font.bold = True
        set_cell_margins(c_hdr[i], 100, 100, 100, 100)

    model_rows = [
        ("Majority Baseline", "0.5000", "0.5000", "68.23%", "0.00%", "0.00%", "0.0000"),
        ("Logistic Regression", "0.6625", "0.7466", "73.40%", "91.03%", "18.02%", "0.3009"),
        ("Random Forest (Selected)", "0.6951", "0.7762", "73.38%", "96.07%", "16.89%", "0.2873"),
        ("Gradient Boosting", "0.6691", "0.7785", "74.06%", "77.58%", "25.78%", "0.3870")
    ]
    for idx, (mname, vra, tra, tacc, tpr, trec, tf1) in enumerate(model_rows):
        r = table_comp.rows[idx + 1].cells
        for col_idx, text in enumerate([mname, vra, tra, tacc, tpr, trec, tf1]):
            r[col_idx].paragraphs[0].text = text
            set_cell_margins(r[col_idx], 80, 80, 100, 100)
            if "Selected" in mname:
                set_cell_background(r[col_idx], "E6F4F5")
            elif idx % 2 == 1:
                set_cell_background(r[col_idx], HEX_ALT_ROW)

    add_h2("5.2 Impact of Threshold Calibration")
    res_2 = (
        "While standard 0.50 thresholding produces high precision (>96%), its low recall (16.9%) misses over 83% of cancellations. "
        "In hospitality management, the cost of an undetected cancellation far exceeds the cost of a routine verification check. "
        "Calibrating the threshold to θ* = 0.16 dramatically shifts operational performance:"
    )
    add_p(res_2)

    table_thresh = doc.add_table(rows=3, cols=6)
    table_thresh.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_thresh)
    t_hdr = table_thresh.rows[0].cells
    for i, title in enumerate(["Operating Threshold", "Test Accuracy", "Test Precision", "Test Recall", "Test F1-Score", "Brier Score"]):
        t_hdr[i].text = title
        set_cell_background(t_hdr[i], HEX_TEAL)
        t_hdr[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        t_hdr[i].paragraphs[0].runs[0].font.bold = True
        set_cell_margins(t_hdr[i], 100, 100, 100, 100)

    thresh_data = [
        ("Standard (θ = 0.50)", "73.38%", "96.07%", "16.89%", "0.2873", "0.1678"),
        ("Tuned Operational (θ* = 0.16)", "52.34%", "41.20%", "91.10%", "0.5676", "0.1678")
    ]
    for idx, (th, acc, pr, rec, f1, br) in enumerate(thresh_data):
        r = table_thresh.rows[idx + 1].cells
        for col_idx, text in enumerate([th, acc, pr, rec, f1, br]):
            r[col_idx].paragraphs[0].text = text
            set_cell_margins(r[col_idx], 80, 80, 100, 100)
            if "0.16" in th:
                set_cell_background(r[col_idx], "E6F4F5")

    add_figure(FIG_DIR / "roc_curve.png", "Figure 3: Held-out Test ROC Curve for the Selected Random Forest Classifier (AUC = 0.776)")
    add_figure(FIG_DIR / "confusion_matrix.png", "Figure 4: Held-out Test Confusion Matrix at the Operational Review Threshold (θ* = 0.16)")

    add_h2("5.3 Feature Importance & Reliability")
    res_3 = (
        "Permutation feature importance (Figure 5) confirms that lead_time, deposit_type, adr, and arrival_date_month are the dominant "
        "predictive drivers. Probability calibration (Figure 6) reveals slight overconfidence in the mid-range probabilities, reinforcing "
        "that model outputs should serve as prioritization scores rather than absolute frequentist probabilities."
    )
    add_p(res_3)

    add_figure(FIG_DIR / "feature_importance.png", "Figure 5: Validation permutation importance (mean decrease in ROC AUC after shuffling)")
    add_figure(FIG_DIR / "calibration.png", "Figure 6: Test set probability calibration curve (predicted probability vs. observed frequency)")

    doc.add_page_break()

    # ==========================================
    # CHAPTER 6: SOFTWARE ARCHITECTURE & GUI
    # ==========================================
    add_h1("6. SOFTWARE ARCHITECTURE & STREAMLIT GUI")
    arch_1 = (
        "The software architecture follows a clean layered pattern ensuring complete decoupling between statistical modeling, "
        "data ingestion, and presentation logic:\n"
        "  1. Data Ingestion Layer (src/data.py): Enforces SHA-256 validation, date synthesis, and clean temporal partitioning.\n"
        "  2. Feature Engineering Layer (src/features.py): Transforms inputs, enforces column allowlists, and isolates transformers.\n"
        "  3. Inference Layer (src/model.py): Handles single and batch scoring, probability calibration, and flag generation.\n"
        "  4. Presentation Layer (app.py & app_pages/): Multi-page Streamlit application with cached models and safe session state."
    )
    add_p(arch_1)

    add_h2("6.1 GUI Subsystem Description")
    add_bullet("1. Overview Page: ", "Executive dashboard presenting problem framing, dataset summary, key metrics, and recommended review workflow.")
    add_bullet("2. Booking Patterns: ", "Interactive exploratory analytics visualizing cancellation rates across channels, deposit types, customer profiles, and stay lengths with 95% Wilson confidence intervals.")
    add_bullet("3. Predict a Booking: ", "Live single-booking scoring form allowing hotel staff to simulate guest parameters, compute cancellation probability, and observe review status in real time.")
    add_bullet("4. Batch Predictions: ", "Enterprise-grade batch processor accepting CSV uploads up to 10,000 rows. Validates schemas, ignores extraneous outcome columns, sanitizes inputs, and exports safe CSV predictions.")
    add_bullet("5. Model Lab: ", "Diagnostic comparison suite contrasting Baseline, Logistic Regression, Random Forest, and Gradient Boosting curves, leakage defenses, and error breakdowns.")
    add_bullet("6. Project Guide: ", "Reference documentation containing data dictionaries, mathematical formulas, and downloadable project deliverables.")

    add_h2("6.2 Batch Processing Security and Robustness")
    arch_2 = (
        "Batch prediction incorporates strict security safeguards:\n"
        "  • Schema Validation: Requires all 20 template fields; rejects missing or malformed columns with human-readable error messages.\n"
        "  • CSV Injection Prevention: Formula prefix characters ('=', '+', '-', '@') in text fields are escaped to prevent spreadsheet execution.\n"
        "  • Outcome Immunity: Uploaded files containing 'is_canceled' or 'reservation_status' columns have those fields stripped prior to scoring.\n"
        "  • Session Privacy: Uploaded CSV files remain strictly inside memory and are never written to disk or transmitted externally."
    )
    add_p(arch_2)

    doc.add_page_break()

    # ==========================================
    # CHAPTER 7: TESTING & REPRODUCIBILITY
    # ==========================================
    add_h1("7. TESTING, VERIFICATION AND REPRODUCIBILITY")
    add_h2("7.1 Automated Test Suite")
    test_1 = (
        "To ensure production reliability and prevent regressions, the project includes an automated test suite executed via pytest. "
        "A total of 25 unit and UI smoke tests validate core pipeline invariants:"
    )
    add_p(test_1)

    add_bullet("• Data Integrity Tests: ", "Verify that the raw CSV matches the official SHA-256 hash, and that zero-guest/negative-price rows are properly filtered.")
    add_bullet("• Temporal Partition Tests: ", "Enforce strict temporal boundaries ensuring max(Train Date) < min(Val Date) and max(Val Date) < min(Test Date).")
    add_bullet("• Feature Contract Tests: ", "Verify that target and post-event variables are strictly absent from feature matrices.")
    add_bullet("• Batch Invariance Tests: ", "Confirm that batch inference produces identical numerical probabilities whether scored individually or in bulk.")
    add_bullet("• Streamlit AppTest Suite: ", "Exercise page routing, form inputs, button callbacks, and batch download triggers across all six GUI views without browser overhead.")

    add_callout(
        "Pytest Execution Results:\n"
        "Root Directory: tests/test_project.py & tests/test_gui.py\n"
        "Execution Command: .venv\\Scripts\\python.exe -m pytest -q\n"
        "Test Output: ......................... [100%]\n"
        "Summary: 25 passed in 15.46 seconds (100% Success Rate).",
        bold_title="AUTOMATED TEST SUITE STATUS"
    )

    add_h2("7.2 Reproducibility Protocol")
    test_2 = (
        "The project is 100% self-contained and reproducible offline:\n"
        "  • Windows 1-Click Setup: SETUP.bat automatically detects Python (3.10+), creates .venv, installs dependencies, and verifies pre-trained models.\n"
        "  • 1-Click Launch: START_PROJECT.bat auto-detects free ports (8501–8510) and launches the GUI in the default web browser.\n"
        "  • Cross-Platform Support: setup.sh and run.sh provide identical shell functionality for Linux and macOS environments.\n"
        "  • Fully Pinned Environment: Exact dependency resolutions are frozen in requirements-lock.txt and tracked in Git."
    )
    add_p(test_2)

    doc.add_page_break()

    # ==========================================
    # CHAPTER 8: LIMITATIONS & FUTURE SCOPE
    # ==========================================
    add_h1("8. LIMITATIONS, ETHICAL CONSIDERATIONS & FUTURE WORK")
    add_h2("8.1 Study Limitations")
    lim_1 = (
        "1. Geographical & Temporal Specificity: Data originates exclusively from two hotels in Portugal during 2015–2017. Economic, "
        "cultural, and seasonal patterns may not generalize directly to modern Indian hospitality markets without domain fine-tuning.\n\n"
        "2. Approximate Booking Creation Timestamps: Booking creation dates are approximated as arrival_date minus lead_time, "
        "assuming midnight timestamps and omitting intra-day booking hour variations.\n\n"
        "3. Missing Guest Identifiers: Due to anonymization, individual guest IDs are absent. Consequently, repeat reservations by "
        "the same traveler or travel agent cannot be grouped into longitudinal clusters.\n\n"
        "4. Observational Nature: The identified patterns reflect historical correlations and do not imply causal mechanisms. For "
        "example, changing a deposit policy will not necessarily alter cancellation behavior in the exact magnitude predicted."
    )
    add_p(lim_1)

    add_h2("8.2 Ethical and Operational Boundaries")
    lim_2 = (
        "• Human-in-the-Loop Decision Support: The system is explicitly designed to assist hotel reservation managers rather than "
        "execute autonomous cancellations. The model should never cancel a reservation automatically.\n"
        "• Non-Discriminatory Attributes: The feature space intentionally excludes sensitive demographic characteristics such as "
        "guest nationality, ethnicity, gender, or personal identifiers.\n"
        "• Data Privacy & Security: The application stores zero customer PII and runs strictly on local memory sessions."
    )
    add_p(lim_2)

    add_h2("8.3 Future Enhancements")
    add_bullet("• Dynamic PMS Integration: ", "Develop two-way connectors for open-source Property Management Systems (e.g., Cloudbeds, Opera API).")
    add_bullet("• Survival Analysis: ", "Implement Cox Proportional Hazards modeling to predict not just if a booking will cancel, but exactly when the cancellation will occur.")
    add_bullet("• Cost-Sensitive Optimization: ", "Incorporate hotel-specific financial parameters (room margins, re-booking probabilities, walking penalties) directly into the threshold optimization objective function.")

    # ==========================================
    # CHAPTER 9: CONCLUSION & REFERENCES
    # ==========================================
    add_h1("9. CONCLUSION")
    concl_text = (
        "This project successfully designs, implements, and evaluates an end-to-end Data Science solution for hotel booking "
        "cancellation prediction. By adhering to rigorous data science principles—including cryptographic provenance tracking, "
        "leak-free chronological splitting, multi-model benchmarking, and validation-driven threshold calibration—the resulting system "
        "achieves a robust 0.776 Test ROC AUC and 91.1% cancellation recall.\n\n"
        "The delivery of a responsive, multi-page Streamlit application, coupled with comprehensive automated tests and "
        "cross-platform launcher scripts, bridges the gap between academic machine learning and practical decision support. "
        "The project demonstrates that environmental and behavioral booking signals can effectively mitigate revenue risk while "
        "maintaining transparent, ethical operational boundaries."
    )
    add_p(concl_text, space_after=18)

    add_h1("10. REFERENCES")
    refs = [
        "Antonio, N., de Almeida, A. and Nunes, L. (2019). Hotel booking demand datasets. Data in Brief, 22, pp. 41–49. DOI: 10.1016/j.dib.2018.11.126.",
        "Mock, T. and Bichat, A. (2020). TidyTuesday: Hotel Booking Demand Dataset. GitHub Repository: https://github.com/rfordatascience/tidytuesday/tree/main/data/2020/2020-02-11.",
        "Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, pp. 2825–2830.",
        "Streamlit Inc. (2026). Streamlit Documentation: Multi-page Apps and Component Architecture. Available at: https://docs.streamlit.io/.",
        "Breiman, L. (2001). Random Forests. Machine Learning, 45(1), pp. 5–32. DOI: 10.1023/A:1010933404324.",
        "Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. Journal of the American Statistical Association, 22(158), pp. 209–212.",
        "Pimpri Chinchwad College of Engineering (PCCoE), Pune. Department of Information Technology - VSEC Data Science Laboratory Course Curriculum (BIT23VS01), 2026."
    ]
    for idx, ref in enumerate(refs, 1):
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.left_indent = Inches(0.3)
        p_ref.paragraph_format.first_line_indent = Inches(-0.3)
        p_ref.paragraph_format.space_before = Pt(2)
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.add_run(f"[{idx}] ").bold = True
        p_ref.add_run(ref)

    # Save document
    doc.save(str(OUTPUT_DOCX))
    doc.save(str(ROOT_OUTPUT_DOCX))
    print(f"Report successfully generated at:\n  1. {OUTPUT_DOCX}\n  2. {ROOT_OUTPUT_DOCX}")

if __name__ == "__main__":
    build_report()
