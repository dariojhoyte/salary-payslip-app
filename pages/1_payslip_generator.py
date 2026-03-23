# --------------------------------------------------
# standard libraries
# --------------------------------------------------
from io import BytesIO

# --------------------------------------------------
# third-party libraries
# --------------------------------------------------
import pandas as pd
import streamlit as st
from pypdf import PdfReader, PdfWriter

# --------------------------------------------------
# project modules
# --------------------------------------------------
from utils.auth import (
    require_auth,
    logout,
)

from utils.helpers import (
    inject_base_styles,
    render_sidebar,
    validate_required_columns,
    validate_rows,
    money,
    clean_filename,
)

from utils.pdf_generator import (
    create_preview_pdf_bytes,
    build_protected_zip,
)

from utils.app_metadata import (
    get_app_name,
    get_app_icon,
    get_app_layout,
)

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title=get_app_name(),
    page_icon=get_app_icon(),
    layout=get_app_layout(),
)

# --------------------------------------------------
# authentication & UI setup
# --------------------------------------------------

# restrict page access to authenticated users only
require_auth()

# apply app global styles 
inject_base_styles()

# render sidebar
render_sidebar()

# handle logout and redirect to login page
if st.sidebar.button("Logout", use_container_width=True):
    logout()
    st.switch_page("main.py")

# --------------------------------------------------
# Constants
# --------------------------------------------------

# required columns headersexpected in uploaded payroll files
REQUIRED_COLUMNS = [
    "employee_id",
    "first_name",
    "last_name",
    "employee_secure_pin",
    "pay_period",
    "hourly_rate",
    "regular_hours",
    "overtime_hours",
    "double_time_hours",
    "overtime_rate",
    "double_time_rate",
    "regular_pay",
    "overtime_pay",
    "double_time_pay",
    "other_pay",
    "vacation_pay",
    "bonus",
    "gross_pay",
    "gross_notes",
    "paye",
    "nis",
    "health_insurance",
    "other_deductions",
    "total_deductions",
    "deductions_notes",
    "net_pay",
    "payment_method",
    "general_payslip_notes",
]

# numeric columns to validate before processing
NUMERIC_COLUMNS = [
    "hourly_rate",
    "regular_hours",
    "overtime_hours",
    "double_time_hours",
    "overtime_rate",
    "double_time_rate",
    "regular_pay",
    "overtime_pay",
    "double_time_pay",
    "other_pay",
    "vacation_pay",
    "bonus",
    "gross_pay",
    "paye",
    "nis",
    "health_insurance",
    "other_deductions",
    "total_deductions",
    "net_pay",
]

# retrieve company details from session state
company = st.session_state.get("company", {})



# --------------------------------------------------
# Functions
# --------------------------------------------------

# build on-screen HTML preview for a single payslip
def render_payslip_preview_html(row):
    employee_name = f"{str(row['first_name']).strip()} {str(row['last_name']).strip()}".strip()
    #employee_name_FLIPPED = f"{str(row['last_name']).strip()} {str(row['first_name']).strip()}".strip()

    TBL_TD_STYLE = "padding: 6px; border-bottom: 1px solid #e5e5e5;font-size: 0.75rem"

    return f'''
    <div style="
        max-width: 720px;
        margin: 0 auto;
        padding: 32px;
        border: 1px solid #dcdcdc;
        border-radius: 10px;
        background: white;
        font-family: Arial, sans-serif;
        color: #222;
        box-sizing: border-box;
    ">
        

        <div style="
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 20px;
        ">

            <!-- LEFT SIDE -->
            <div>
                <h2 style="margin: 0;">{company.get('name', 'Company')}</h2>
                <h3 style="margin: 4px 0 0 0; font-weight: 600;">Salary Payslip</h3>
            </div>

            <!-- RIGHT SIDE -->
            <div style="text-align: right;">
                <span style="color: #666; font-size: 0.9em;"></span>
            </div>

        </div>

        <div style="margin-bottom: 10px;">
            <h4 style="margin-bottom: 10px;">Employee Information</h4>
            <div style="border: 1px solid #dcdcdc; border-radius: 8px; padding: 14px; line-height: 1.4; font-size: 0.85rem;">
                <div><strong>Employee ID:</strong> {row['employee_id']}</div>
                <div><strong>Employee Name:</strong> {employee_name}</div>
                <div><strong>Pay Period:</strong> {pd.to_datetime(row['pay_period']).strftime("%Y-%b-%d")}</div>
                <div><strong>Payment Method:</strong> {row['payment_method']}</div>
                <div><strong>Base Rate/hr:</strong> {money(row['hourly_rate'])}</div>
            </div>
        </div>

       <div style="
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            font-size: 0.85rem;
        ">
            <div style="flex: 1;">
                <div style="margin-bottom: 15px;">
                    <h4 style="margin-bottom: 10px;">Earnings</h4>
                    <table style="width: 100%; border-collapse: collapse; border: 1px solid #dcdcdc;">
                        <tr>
                            <td style="{TBL_TD_STYLE}">
                                <strong>Regular Pay</strong><span style='font-size:0.8em; color:gray;'>, {row['regular_hours']}hr(s)</span>
                            </td>
                            <td style="{TBL_TD_STYLE}">{money(row['regular_pay'])}</td>
                        </tr>
                        <tr>
                            <td style="{TBL_TD_STYLE}">
                                <strong>Overtime Pay (x1.5)</strong><span style='font-size:0.8em; color:gray;'>, {row['overtime_hours']}hr(s)</span>
                            </td>
                            <td style="{TBL_TD_STYLE}">{money(row['overtime_pay'])}</td>
                        </tr>
                        <tr>
                            <td style="{TBL_TD_STYLE}">
                                <strong>Double Time Pay (x2.0)</strong><span style='font-size:0.8em; color:gray;'>, {row['double_time_hours']}hr(s)</span>
                            </td>
                            <td style="{TBL_TD_STYLE}">{money(row['double_time_pay'])}</td>
                        </tr>
                        <tr>
                            <td style="{TBL_TD_STYLE}"><strong>Other Pay</strong></td>
                            <td style="{TBL_TD_STYLE}">{money(row['other_pay'])}</td>
                        </tr>
                        <tr>
                            <td style="{TBL_TD_STYLE}"><strong>Vacation Pay</strong></td>
                            <td style="{TBL_TD_STYLE}">{money(row['vacation_pay'])}</td>
                        </tr>
                        <tr>
                            <td style="{TBL_TD_STYLE}"><strong>Bonus</strong></td>
                            <td style="{TBL_TD_STYLE}">{money(row['bonus'])}</td>
                        </tr>
                        <tr style="background: #f8f9fa;">
                            <td style="padding: 12px;"><strong>Gross Pay</strong></td>
                            <td style="padding: 12px;"><strong>{money(row['gross_pay'])}</strong></td>
                        </tr>
                    </table>
                </div>
            </div>

            <div style="flex: 1;">
                <div style="margin-bottom: 15px;">
                    <h4 style="margin-bottom: 10px;">Deductions</h4>
                    <table style="width: 100%; border-collapse: collapse; border: 1px solid #dcdcdc;">
                        <tr>
                            <td style="{TBL_TD_STYLE}"><strong>PAYE</strong></td>
                            <td style="{TBL_TD_STYLE}">{money(row['paye'])}</td>
                        </tr>
                        <tr>
                            <td style="{TBL_TD_STYLE}"><strong>NIS</strong></td>
                            <td style="{TBL_TD_STYLE}">{money(row['nis'])}</td>
                        </tr>
                        <tr>
                            <td style="{TBL_TD_STYLE}"><strong>Health Insurance</strong></td>
                            <td style="{TBL_TD_STYLE}">{money(row['health_insurance'])}</td>
                        </tr>
                        <tr>
                            <td style="{TBL_TD_STYLE}"><strong>Other Deductions</strong></td>
                            <td style="{TBL_TD_STYLE}">{money(row['other_deductions'])}</td>
                        </tr>
                        <tr>
                            <td style="{TBL_TD_STYLE}"><strong>-</strong></td>
                            <td style="{TBL_TD_STYLE}"></td>
                        </tr>
                        <tr>
                            <td style="{TBL_TD_STYLE}"><strong>-</strong></td>
                            <td style="{TBL_TD_STYLE}"></td>
                        </tr>
                        <tr style="background: #f8f9fa;">
                            <td style="padding: 12px;"><strong>Total Deductions</strong></td>
                            <td style="padding: 12px;"><strong>{money(row['total_deductions'])}</strong></td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>

        <div style="margin-bottom: 24px;">            
            <div style="border: 1px solid #dcdcdc; border-radius: 8px; padding: 14px; line-height: 1.8; background: #f8f9fa;">
                <div><strong>Net Pay:</strong> {money(row['net_pay'])}</div>
            </div>
        </div>

        <p style="font-size: 12px; color: #666; margin-top: 20px;">
            <strong>Earnings Notes:</strong> {row.get('gross_notes', '')}
        </p>
        <p style="font-size: 12px; color: #666; margin-top: 8px;">
            <strong>Deduction Notes:</strong> {row.get('deductions_notes', '')}
        </p>
        <p style="font-size: 12px; color: #666; margin-top: 8px;">
            <strong>General Notes:</strong> {row.get('general_payslip_notes', '')}
        </p>
        <p style="font-size: 12px; color: #666; margin-top: 30px;">
            This is a system-generated payslip.
        </p>
    </div>
    '''

# apply password protection to generated PDF bytes
def add_pdf_password(pdf_bytes, password):
    input_buffer = BytesIO(pdf_bytes)
    output_buffer = BytesIO()

    reader = PdfReader(input_buffer)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)

    writer.write(output_buffer)
    output_buffer.seek(0)

    return output_buffer.getvalue()



# --------------------------------------------------
# 'Payslip Generator' page content
# --------------------------------------------------
st.title("Payslip Generator")
st.caption("Upload payroll data, preview individual payslips, and download password-protected PDFs as a ZIP file.")

st.markdown("---")

st.header("1. Upload Payroll File")

# accept user payroll upload (CSV or xlsx)
uploaded_file = st.file_uploader("Upload payroll file (CSV or Excel)", type=["xlsx", "csv"])

if uploaded_file:

    # error handling
    try:
        # read uploaded file into DataFrame
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("Uploaded Data")
        st.dataframe(df, use_container_width=True)


        # validate required column structure
        missing = validate_required_columns(df, REQUIRED_COLUMNS)
        if missing:
            st.error(f"Missing columns: {', '.join(missing)}")
            st.stop()

        # validate row-level values and data types
        row_errors = validate_rows(df, REQUIRED_COLUMNS, NUMERIC_COLUMNS)
        if row_errors:
            st.error("Validation failed.")
            for err in row_errors[:20]:
                st.write(f"- {err}")
            if len(row_errors) > 20:
                st.write(f"...and {len(row_errors) - 20} more")
            st.stop()

        st.success("File validated successfully.")

        st.markdown("---")

        st.header("2. Data and payslip preview")

        # prepare employee dataset preview
        preview_df = df.copy()
        preview_df["employee_name"] = (
            preview_df["first_name"].fillna("").astype(str).str.strip()
            + " "
            + preview_df["last_name"].fillna("").astype(str).str.strip()
        ).str.strip()

        #sort values populating drop box by last name first, then first name
        preview_df = preview_df.sort_values(by=["last_name", "first_name"])


        # display label for preview dropdown
        preview_df["Preview Label"] = preview_df.apply(
            lambda row: f"{row['last_name']}, {row['first_name']} | ID: {row['employee_id']} | Pay Period: {pd.to_datetime(row['pay_period']).strftime("%Y-%b-%d")}",
            axis=1,
        )

        st.subheader("Single Payslip Preview")
        
        # select employee for preview       
        selected_label = st.selectbox(
            "Select an employee to preview (sorted by last name)",
            preview_df["Preview Label"].tolist(),
        )

        # retrieve selected employee row
        selected_row = preview_df.loc[preview_df["Preview Label"] == selected_label].iloc[0]

        # generate preview PDF data
        preview_pdf_bytes = create_preview_pdf_bytes(selected_row)

        # use control to optionally apply password protection to single PDF (the previewed one) on download
        protect_pdf = st.checkbox("🔒 Password protect PDF", value=True)

        # build system-generated password
        preview_password = (
            f"{str(selected_row['first_name'])[:1].lower()}"
            f"{str(selected_row['last_name'])[:1].lower()}"
            f"{str(selected_row['employee_secure_pin'])}!"
        )

        pdf_bytes = preview_pdf_bytes

        #if user selects to password protect single PDF file download, 
        # -then, add password to pdf, 
        # -else, remove password
        if protect_pdf:
            pdf_bytes = add_pdf_password(pdf_bytes, preview_password)

        

        # display password only when protection is enabled
        if protect_pdf:
            st.markdown(
                f"<div style='text-align:left; margin-bottom: 20px;'><b>Generated PDF Password:</b> {preview_password}</div>",
                unsafe_allow_html=True
            )

        # build clean downloadable filename
        STR_FILENAME = (f"{selected_row['last_name']} {selected_row['first_name']} "
                        f"ID {selected_row['employee_id']} Period {pd.to_datetime(selected_row['pay_period']).strftime("%Y-%m-%d")}")
        

        # download selected payslip PDF button/action
        st.download_button(
            label="Download Selected Payslip (PDF)",
            data=pdf_bytes,
            file_name=f"Payslip_{clean_filename(STR_FILENAME)}.pdf",
            mime="application/pdf",
        )

        # render HTML preview on page
        st.markdown(
                "<div style='text-align:center;;'>Payslip Preview</div>",
                unsafe_allow_html=True
            )
        st.components.v1.html(
            render_payslip_preview_html(selected_row),            
            height=500,
            scrolling=True,
        )
        st.success("Preview generated successfully.")


        st.markdown("---")


        st.header("3. Download All Payslips (ZIP)")

        st.write("All payslips are generated, password-protected, and downloaded as a ZIP file.")

        # generate ZIP containing all protected payslips
        zip_bytes = build_protected_zip(df)


        # download ZIP archive
        st.download_button(
            label="Download All Protected Payslips (ZIP)",
            data=zip_bytes,
            file_name="protected_payslips.zip",
            mime="application/zip",
        )

    #catch error
    except Exception as e:
        st.error(f"Error reading file: {e}")