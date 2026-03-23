"""
PDF generation utilities

purpose:
- rendering payslips as PDF documents
- generating password-protected PDFs
- packaging batch-generated payslips into a ZIP archive

Dev notes:
- company details are read from Streamlit session state
- uses ReportLab for PDF rendering
- uses PyPDF for PDF encryption
- batch-generated PDFs are always password-protected before zipping
"""

# --------------------------------------------------
# standard libraries
# --------------------------------------------------
import io
import zipfile
from datetime import datetime

# --------------------------------------------------
# third-party libraries
# --------------------------------------------------
import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

# --------------------------------------------------
# project modules
# --------------------------------------------------
from utils.helpers import money, clean_filename


# session-based and other variables
company = st.session_state.get("company", {})
COMPANY_NAME = f"{company.get('name', 'Company')}"
PAYSLIP_TITLE = "Salary Payslip"


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

# build full employee name from first and last name fields
def build_employee_name(row):
    first_name = str(row.get("first_name", "")).strip()
    last_name = str(row.get("last_name", "")).strip()
    return f"{first_name} {last_name}".strip()


# build system-generated PDF password
def build_pdf_password(row):
    first_initial = str(row.get("first_name", "")).strip()[:1].lower()
    last_initial = str(row.get("last_name", "")).strip()[:1].lower()
    pin = str(row.get("employee_secure_pin", "")).strip()
    return f"{first_initial}{last_initial}{pin}!"


# --------------------------------------------------
# payslip renderer
# --------------------------------------------------

# draw a single payslip onto a ReportLab canvas
def draw_payslip(c, row):
    from reportlab.lib.colors import HexColor, black

    width, height = LETTER
    employee_name = build_employee_name(row)

    # layout colors
    BORDER = HexColor("#dcdcdc")
    LIGHT_BG = HexColor("#f8f9fa")
    TEXT = HexColor("#222222")
    MUTED = HexColor("#666666")

    # page layout bounds
    PAGE_X = 40
    PAGE_Y = 40
    PAGE_W = width - 80
    PAGE_H = height - 80

    # draw label and value pair on one line
    def draw_label_value(label, value, x, y, label_font="Helvetica-Bold", value_font="Helvetica"):
        c.setFillColor(TEXT)
        c.setFont(label_font, 9)
        c.drawString(x, y, f"{label}")
        label_width = c.stringWidth(label, label_font, 9)
        c.setFont(value_font, 9)
        c.drawString(x + label_width + 4, y, str(value))

    # draw earnings or deductions table
    def draw_table(x, top_y, table_width, title, rows, total_label=None, total_value=None):
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x, top_y, title)

        table_top = top_y - 12
        row_h = 24
        total_rows = len(rows) + (1 if total_label else 0)
        table_h = row_h * total_rows
        value_col_x = x + table_width - 110

        # outer border
        c.setStrokeColor(BORDER)
        c.setLineWidth(1)
        c.rect(x, table_top - table_h, table_width, table_h)

        # inner row lines
        for i in range(1, total_rows):
            yy = table_top - (i * row_h)
            c.line(x, yy, x + table_width, yy)

        # draw data rows
        y_cursor = table_top - 17
        for label, value, subtext in rows:
            c.setFillColor(TEXT)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(x + 8, y_cursor, label)

            if subtext:
                label_w = c.stringWidth(label, "Helvetica-Bold", 9)
                c.setFillColor(MUTED)
                c.setFont("Helvetica", 8)
                c.drawString(x + 8 + label_w + 4, y_cursor, subtext)

            c.setFillColor(TEXT)
            c.setFont("Helvetica", 9)
            c.drawRightString(x + table_width - 8, y_cursor, str(value))
            y_cursor -= row_h

        # total row
        if total_label:
            total_y_top = table_top - (len(rows) * row_h)

            c.setFillColor(LIGHT_BG)
            c.rect(x, total_y_top - row_h, table_width, row_h, stroke=0, fill=1)

            c.setStrokeColor(BORDER)
            c.rect(x, total_y_top - row_h, table_width, row_h, stroke=1, fill=0)

            c.setFillColor(TEXT)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(x + 8, total_y_top - 16, total_label)
            c.drawRightString(x + table_width - 8, total_y_top - 16, str(total_value))

        return table_top - table_h



    y = height - 55

    # header
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(PAGE_X + 18, y, COMPANY_NAME)

    c.setFont("Helvetica-Bold", 13)
    c.drawString(PAGE_X + 18, y - 20, PAYSLIP_TITLE)

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    #preview_text = "Preview"
    #c.drawRightString(PAGE_X + PAGE_W - 18, y - 5, preview_text)

    y -= 48

    # employee information
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(PAGE_X + 18, y, "Employee Information")

    info_top = y - 10
    info_h = 78

    c.setStrokeColor(BORDER)
    c.roundRect(PAGE_X + 18, info_top - info_h, PAGE_W - 36, info_h, 8, stroke=1, fill=0)

    info_x = PAGE_X + 30
    line_y = info_top - 16
    gap = 14

    draw_label_value("Employee ID:", row["employee_id"], info_x, line_y)
    line_y -= gap
    draw_label_value("Employee Name:", employee_name, info_x, line_y)
    line_y -= gap
    draw_label_value("Pay Period:", pd.to_datetime(row["pay_period"]).strftime("%Y-%b-%d"), info_x, line_y)
    line_y -= gap
    draw_label_value("Payment Method:", row["payment_method"], info_x, line_y)
    line_y -= gap
    draw_label_value("Base Rate/hr:", money(row["hourly_rate"]), info_x, line_y)

    y = info_top - info_h - 26


    # earnings and deductions side by side
    gap_between = 16
    col_w = (PAGE_W - 36 - gap_between) / 2
    left_x = PAGE_X + 18
    right_x = left_x + col_w + gap_between

    earnings_rows = [
        ("Regular Pay", money(row["regular_pay"]), f", {row['regular_hours']}hr(s)"),
        ("Overtime Pay (x1.5)", money(row["overtime_pay"]), f", {row['overtime_hours']}hr(s)"),
        ("Double Time Pay (x2.0)", money(row["double_time_pay"]), f", {row['double_time_hours']}hr(s)"),
        ("Other Pay", money(row["other_pay"]), ""),
        ("Vacation Pay", money(row["vacation_pay"]), ""),
        ("Bonus", money(row["bonus"]), ""),
    ]

    deductions_rows = [
        ("PAYE", money(row["paye"]), ""),
        ("NIS", money(row["nis"]), ""),
        ("Health Insurance", money(row["health_insurance"]), ""),
        ("Other Deductions", money(row["other_deductions"]), ""),
        ("-", "", ""),
        ("-", "", ""),
    ]

    left_bottom = draw_table(
        left_x,
        y,
        col_w,
        "Earnings",
        earnings_rows,
        total_label="Gross Pay",
        total_value=money(row["gross_pay"]),
    )

    right_bottom = draw_table(
        right_x,
        y,
        col_w,
        "Deductions",
        deductions_rows,
        total_label="Total Deductions",
        total_value=money(row["total_deductions"]),
    )

    y = min(left_bottom, right_bottom) - 22

    
    # net pay
    c.setFillColor(LIGHT_BG)
    net_h = 34
    c.roundRect(PAGE_X + 18, y - net_h, PAGE_W - 36, net_h, 8, stroke=0, fill=1)
    c.setStrokeColor(BORDER)
    c.roundRect(PAGE_X + 18, y - net_h, PAGE_W - 36, net_h, 8, stroke=1, fill=0)

    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(PAGE_X + 30, y - 21, f"Net Pay: {money(row['net_pay'])}")

    y -= 54


    # notes
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8.5)

    gross_notes = str(row.get("gross_notes", "")).strip()
    deduction_notes = str(row.get("deductions_notes", "")).strip()
    general_notes = str(row.get("general_payslip_notes", "")).strip()

    c.drawString(PAGE_X + 18, y, f"Earnings Notes: {gross_notes}")
    y -= 14
    c.drawString(PAGE_X + 18, y, f"Deduction Notes: {deduction_notes}")
    y -= 14
    c.drawString(PAGE_X + 18, y, f"General Notes: {general_notes}")
    y -= 22

    c.drawString(PAGE_X + 18, y, f"This is a system-generated payslip. Generated on {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")


# --------------------------------------------------
# PDF byte generators
# --------------------------------------------------

# create unprotected PDF bytes for a single payslip
def create_plain_pdf_bytes(row) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    draw_payslip(c, row)
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# apply password protection to PDF bytes
def encrypt_pdf_bytes(pdf_bytes: bytes, password: str) -> bytes:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(str(password))

    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out.getvalue()

# create preview PDF bytes without password protection
def create_preview_pdf_bytes(row) -> bytes:
    return create_plain_pdf_bytes(row)


# --------------------------------------------------
# ZIP function
# --------------------------------------------------

# build ZIP archive containing protected payslips for all employees
def build_protected_zip(df) -> bytes:
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for _, row in df.iterrows():
            plain_pdf = create_plain_pdf_bytes(row)

            protected_pdf = encrypt_pdf_bytes(
                plain_pdf,
                build_pdf_password(row),
            )

            employee_name = clean_filename(build_employee_name(row))
            employee_id = clean_filename(row["employee_id"])
            pay_period = clean_filename(row["pay_period"])

            filename = f"Payslip_{employee_name}_{employee_id}_{pay_period}.pdf"
            zf.writestr(filename, protected_pdf)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()