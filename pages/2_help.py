# --------------------------------------------------
# standard libraries
# --------------------------------------------------
# none

# --------------------------------------------------
# third-party libraries
# --------------------------------------------------
import pandas as pd
import streamlit as st

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
)

from utils.app_metadata import (
    get_app_name,
    get_app_icon,
    get_app_layout,
    get_app_version,
    get_author_name,
    get_author_url,
)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
# configure the page layout and appearance
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
# 'Help' page content 
# --------------------------------------------------
st.title("Help")
st.caption("User guide, file requirements, and support information.")

# separator
st.markdown("---")

# basic usage steps for users
st.subheader("How to Use Payslip Generator")
st.write(
    "1. **Sign in** with your admin credentials.  \n"
    "2. **Open** the Payslip Generator page.  \n"
    "3. **Upload** your payroll file in Excel or CSV format.  \n"
    "4. **Review** the data preview and sample output.  \n"
    "5. **Download** the ZIP file containing the generated password-protected PDFs.  \n"
)

# separator
st.markdown("---")

# example of required file format
st.subheader("Payroll File - Required Header Format")
st.write("Columns are exported in CSV batch format from the ASM ERP system. These columns are static and should not be modified.")
st.code(
    "COL 1: employee_id\n"
    "COL 2: first_name\n"
    "COL 3: last_name\n"
    "COL 4: employee_secure_pin\n"
    "COL 5: pay_period\n"
    "COL 6: hourly_rate\n"
    "COL 7: regular_hours\n"
    "COL 8: overtime_hours\n"
    "COL 9: double_time_hours\n"
    "COL 10: overtime_rate\n"
    "COL 11: double_time_rate\n"
    "COL 12: regular_pay\n"
    "COL 13: overtime_pay\n"
    "COL 14: double_time_pay\n"
    "COL 15: other_pay\n"
    "COL 16: vacation_pay\n"
    "COL 17: bonus\n"
    "COL 18: gross_pay\n"
    "COL 19: gross_notes\n"
    "COL 20: paye\n"
    "COL 21: nis\n"
    "COL 22: health_insurance\n"
    "COL 23: other_deductions\n"
    "COL 24: total_deductions\n"
    "COL 25: deductions_notes\n"
    "COL 26: net_pay\n"
    "COL 27: payment_method\n"
    "COL 28: general_payslip_notes\n",
    language="csv",
)

# sample data displayed in a dataframe
st.write("**Sample Data (truncated for display):**")
example_df = pd.DataFrame([
    {
        "employee_id": 2001,
        "first_name": "Lucas",
        "last_name": "Martinez",
        "employee_secure_pin": 8891,
        "pay_period": "4/15/2026",
        "hourly_rate": 27,
        "regular_hours": 76,
        "overtime_hours": 8,
        "gross_pay": 2300,
        "total_deductions": 550,
        "net_pay": 1750,
        "payment_method": "Direct Deposit",
        "bonus": 120,
        "...": "..."
    },
    {
        "employee_id": 2002,
        "first_name": "Emma",
        "last_name": "Chen",
        "employee_secure_pin": 4422,
        "pay_period": "4/15/2026",
        "hourly_rate": 31,
        "regular_hours": 72,
        "overtime_hours": 6,
        "gross_pay": 2500,
        "total_deductions": 600,
        "net_pay": 1900,
        "payment_method": "Cheque",
        "bonus": 150,
        "...": "..."
    }
])
st.dataframe(example_df, use_container_width=True, hide_index=True)



# separator
st.markdown("---")

# pdf export notes
st.subheader("PDF Export Notes")
st.write(    
    "Each generated payslip can be optionally password-protected using the system-generated format below. "
    "All batch-generated payslips are password-protected and downloaded as a ZIP file.  \n"
    "Format: ***first initial*** + ***last initial*** + ***4-digit PIN*** + '!'  \n\n"
    "**Example:**  \n"
    "Employee John Smith with a 4-digit PIN of '1234' (from the CSV export) results in the PDF password **js1234!**  \n"
    "*Note, the exclamation mark is part of the password."
)

# separator
st.markdown("---")

st.subheader("Security")
st.write(
    "User authentication is secured using industry-standard PBKDF2 password hashing."
)

# separator
st.markdown("---")

# app info / credits
st.subheader("About")
st.write(f"Developed by {get_author_name()}  \n"
        f"Version {get_app_version()}  \n"
        f"URL: {get_author_url()}")

