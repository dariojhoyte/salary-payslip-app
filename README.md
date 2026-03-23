# Salary Payslip App

A lightweight Streamlit application designed to generate professional, password-protected employee payslips from CSV data exported from external ERP systems.

---

## Project Overview

The client requires software that can generate and download PDF payslips for approximately **30–35 employees**, with the ability to scale for additional companies in the future.

Employee payroll data is sourced from an **online ERP system** that:
- Does **not support printing or emailing payslips**
- Only allows **batch export in CSV format**
- Cannot be replaced at this time
- Does **not provide a local database**

This application bridges that gap by converting exported CSV data into structured, secure payslip PDFs.

---

## Requirements

- Python 3.9 or higher must be installed on the system
- Internet connection required for dashboard features (weather/location APIs)

---

## Core Deliverables

### 1. Login Page
- Secure authentication for:
  - HR
  - Finance
  - Payroll personnel  
- Designed to support **additional users in future**

---

### 2. Dashboard Page
- Clean, simple UI
- Displays:
  - Current date
  - User location
  - Weather (via API)
  - Quick-access information

---

### 3. Payslip Generator (Core Functionality)
- Upload CSV exported from ERP system (static template)
- Automatically generate payslips
- Preview individual payslips before download
- Export single or batch PDFs
- Password protection format:
```
  first initial + last initial + employee PIN + !
```
  Example - Employee Dario Hoyte, with chosen pin '1234' will result in a system generated password:
```
  dh1234!
```
---

### 4. Help Page
- Clear user instructions
- CSV format guidance
- Example templates

---

## Key Features

* Upload payroll data via CSV
* Preview individual payslips
* Generate password-protected PDFs
* Download single or batch payslips
* Company branding support
* Built-in help and documentation
* Secure authentication (PBKDF2 hashing)

---

## Project Structure
```
salary_payslip_app/  
│  
├── main.py — App entry point (login and navigation)  
│  
├── config/  
│   ├── auth_config.json — User authentication (PBKDF2 hashed passwords)  
│   └── company_config.json — Company details and branding  
│  
├── pages/  
│   ├── 1_payslip_generator.py — Core functionality  
│   └── 2_help.py — Help and documentation  
│  
├── utils/  
│   ├── app_metadata.py — App constants  
│   ├── auth.py — Authentication logic  
│   ├── company.py — Company config loader  
│   ├── helpers.py — Utility functions  
│   └── pdf_generator.py — PDF generation logic  
│  
├── assets/  
│   └── logos/  
│       └── logo_air_barbados.png — Company logo  
```
---

## CSV Format (Required Columns)

employee_id, first_name, last_name, employee_secure_pin, pay_period, hourly_rate, regular_hours, overtime_hours, ...

Refer to the **Help page inside the app** for full structure and examples.

A sample file has been provided in the root folder:
SAMPLE_DATA.xlsx

---

## Getting Started

### 1. Install Python (if not already installed)
Download from: https://www.python.org/downloads/

### 2. Install Dependencies
```
pip install streamlit pandas reportlab pypdf requests openpyxl
```

### 3. Run the App
```
streamlit run main.py
```

### 4. Test with Data
You can use the provided sample file in root folder:
SAMPLE_DATA.xlsx

---

## Authentication

- Stored in: config/auth_config.json
- Passwords secured using **PBKDF2 hashing**
- Lightweight approach (no database required)
- Easily scalable for additional users

### Test Credentials (For Demo / Testing Only)

Below are the passwords for:
- HR Admin:
    ```
    hr123 
    ``` 
- Finance Admin
    ```
    finance123
    ```  
- Payroll Admin
    ```
    payroll123
    ```  

Note: these credentials are for testing purposes.
---

## PDF Generation

- Built using **ReportLab**
- Password protection via **PyPDF**
- Secure employee-specific password format

---

## Tech Stack

* Python
* Streamlit (Pyhton UI Framework)
* HTML
* JSON

---

## Notes

- Designed to be **simple, lightweight, and portable**
- User-friendly interface for non-technical staff
- No dependency on external databases
- Scalable for:
  - More users
  - Multiple companies
- Caching implemented to:
  - Reduce API calls
  - Improve performance

---

## Development Notes

- Built using:
  - Python (backend)
  - Streamlit (UI framework)
  - HTML (rendering enhancements)
- JSON used for:
  - Authentication storage
  - Company configuration
- PBKDF2 hashing ensures secure credential storage
- Dashboard integrates external API calls (e.g., weather)
- Caching used for performance optimization

---

## Future Recommendations

- Auto-email generated payslips to employees
- Maintain a registry/log of emailed payslips
- Add audit trail for payroll generation activity
- Role-based access control (RBAC)
- Multi-company switching within UI
- Scheduled/automated payroll processing
- Cloud or shared drive deployment option

---

## Author

Dario J Hoyte
