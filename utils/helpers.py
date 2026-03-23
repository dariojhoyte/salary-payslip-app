"""
Helper utilities

purpose:
- shared helper functions used across the application, including:
    - formatting helpers
        - filename sanitization and formatting
        - currency formatting
    - validation helpers
        - data validation (e.g required columns, numeric validations, date validations etc) for uploaded payroll files
        -
    - payroll helpers
        - payroll date schedule calculations
        -
    - UI helpers
        - UI styling
        - sidebar rendering
    - API helpers
        - location utilities 
        - weather utilities
-

Dev notes:
- includes both UI and data-processing helpers (kept centralized for simplicity)
- external API calls (location, weather) are cached for performance
- validation functions designed to prevent downstream processing errors
"""

# --------------------------------------------------
# standard libraries
# --------------------------------------------------
from datetime import date, timedelta, datetime
import re
import unicodedata
from pathlib import Path

# --------------------------------------------------
# third-party libraries
# --------------------------------------------------
import streamlit as st
import requests
import pandas as pd

# --------------------------------------------------
# project modules
# --------------------------------------------------
from utils.app_metadata import (
    get_app_name,
    get_app_version,
)



# --------------------------------------------------
# formatting helpers
# --------------------------------------------------

# clean string for safe filename usage
def clean_filename(value):
    value = str(value).strip()
    # Normalize unicode → ASCII (é → e)
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    # Remove invalid characters
    value = re.sub(r"[^\w\s-]", "", value)
    # Replace spaces with underscore
    value = re.sub(r"\s+", "_", value)
    # Collapse multiple underscores
    value = re.sub(r"_+", "_", value)
    return value.strip("_")

# format numeric value as currency
def money(value):
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


# --------------------------------------------------
# validation helpers
# --------------------------------------------------

# check for missing required columns
def validate_required_columns(df, required_columns):
    return [col for col in required_columns if col not in df.columns]

# validate date values
def is_valid_excel_date(value):
    
    # accepts 'real' dates/date objects values
    if value is None or str(value).strip() == "" or str(value).lower() == "nan":
        return False
    
    #error handling
    try:
        parsed = pd.to_datetime(value, errors="coerce")
        return not pd.isna(parsed)
    except Exception:
        return False

# validate row/source data integrity
def validate_rows(df, required_columns, numeric_columns):
    errors = []
    for idx, row in df.iterrows():
        excel_row = idx + 2

        # validate required fields
        for col in required_columns:
            if col not in row.index or row[col] is None or str(row[col]).strip() == "" or str(row[col]).lower() == "nan":
                errors.append(f"Row {excel_row}: '{col}' is blank.")

        # numeric validation
        for col in numeric_columns:
            try:
                float(row[col])
            except (ValueError, TypeError, KeyError):
                errors.append(f"Row {excel_row}: '{col}' must be numeric.")

        # validate date period as date
        if "pay_period" in row.index and not is_valid_excel_date(row["pay_period"]):
            errors.append(f"Row {excel_row}: 'pay_period' must be a valid date.")
    return errors


# --------------------------------------------------
# payroll helpers
# --------------------------------------------------

# generate upcoming biweekly payroll dates
def next_biweekly_dates(base_date: date = None, count: int = 4):
    today = date.today()

    # Use provided base_date or fallback reference date
    # future consideration: store base date in company config per company, and even frequency details/variations
    current = base_date or date(2026, 1, 2)

    # perform step-fowards until first date after 'today/now'
    while current < today:
        current += timedelta(days=14)

    # return next N (count) payroll dates after the determined 'current' date
    return [current + timedelta(days=14 * i) for i in range(count)]




# --------------------------------------------------
# UI helpers
# --------------------------------------------------

# global CSS styles for app
def inject_base_styles():
    st.markdown(
        """
        <style>
        .stApp {
            background: white;
        }
        .login-title {
            text-align: center;
            padding-top: 2.5rem;
            padding-bottom: 1rem;
        }
        .login-card, .soft-card {
            background: white;
            border: 1px solid #e6ebf2;
            border-radius: 18px;
            padding: 1.4rem 1.4rem 1.2rem 1.4rem;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04);
        }
        .login-badge, .eyebrow {
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 999px;
            background: #eef4ff;
            color: #274c9b;
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }
        .login-subtitle {
            color: #5f6b7a;
            margin-top: 0.25rem;
        }
        .metric-card {
            background: white;
            border: 1px solid #e6ebf2;
            border-radius: 16px;
            padding: 1rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
            min-height: 110px;
        }
        .metric-title {
            color: #6b7280;
            font-size: 0.9rem;
            margin-bottom: 0.35rem;
        }
        .metric-value {
            font-size: 1.2rem;
            font-weight: 700;
            color: #111827;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# render sidebar with branding and various information
def render_sidebar():
    # display app name and version on siderbar
    #st.sidebar.markdown(f"## {get_app_name()} (v{get_app_version()})")
    st.sidebar.markdown(
        f"## {get_app_name()} <span style='font-size:0.7em; color:gray;'>(v{get_app_version()})</span>",
        unsafe_allow_html=True
    )
    
    # dsplay company name and logo on siderbar
    company = st.session_state.get("company", {})
    logo = company.get("logo")

    # display logo if file exists
    if logo and Path(logo).exists():
        st.sidebar.image(logo, width=120)


    # company info
    st.sidebar.markdown(
        f"""
        <div style="font-size: 0.9rem;">
            {company.get('name')} and its affiliates reserve the rights to this software.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("---")


    # session information detail block
    st.sidebar.markdown(
        f"""
        <div style="
            background-color:#d4edda;
            padding:10px;
            border-radius:8px;
        ">
            <div style="font-size: 1rem;">
                <b>Session Info</b>
            </div>
            <div style="font-size: 0.8rem;">
                Logged in as <b>{st.session_state.get("display_name", "Unknown")}</b><br>
                Login Time (UTC): <b>{st.session_state.get("login_time", "N/A")}</b><br>
                Host Name: <b>{st.session_state.get("host_name", "N/A")}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )





# --------------------------------------------------
# API helpers
# --------------------------------------------------

# map weather code icons and labels
WEATHER_CODE_MAP = {
    0: ("☀️", "Clear"),
    1: ("🌤️", "Mostly Clear"),
    2: ("⛅", "Partly Cloudy"),
    3: ("☁️", "Overcast"),
    45: ("🌫️", "Fog"),
    48: ("🌫️", "Rime Fog"),
    51: ("🌦️", "Light Drizzle"),
    53: ("🌦️", "Drizzle"),
    55: ("🌧️", "Heavy Drizzle"),
    61: ("🌦️", "Light Rain"),
    63: ("🌧️", "Rain"),
    65: ("🌧️", "Heavy Rain"),
    71: ("🌨️", "Light Snow"),
    73: ("❄️", "Snow"),
    75: ("❄️", "Heavy Snow"),
    80: ("🌦️", "Rain Showers"),
    81: ("🌧️", "Rain Showers"),
    82: ("⛈️", "Heavy Showers"),
    95: ("⛈️", "Thunderstorm"),
}

# retrieve user location based on IP (cached)
@st.cache_data(ttl=600)
def get_user_location():
    fallback = {
        "city": "Toronto",
        "region": "ON",
        "country_name": "Canada",
        "latitude": 43.65107,
        "longitude": -79.347015,
    }

    #error handling
    try:
        res = requests.get("https://ipapi.co/json/", timeout=5)
        res.raise_for_status()
        data = res.json()

        lat = data.get("latitude")
        lon = data.get("longitude")

        if lat is None or lon is None:
            return fallback

        return {
            "city": data.get("city", "Toronto"),
            "region": data.get("region_code") or data.get("region", "ON"),
            "country_name": data.get("country_name", "Canada"),
            "latitude": lat,
            "longitude": lon,
        }
    except Exception:
        return fallback

# retrieve weather data from API (cached)
@st.cache_data(ttl=600)
def get_weather(latitude, longitude):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        "&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m"
        "&daily=weather_code,temperature_2m_max,temperature_2m_min"
        "&forecast_days=3"
        "&timezone=auto"
    )

    #error handling
    try:
        res = requests.get(url, timeout=8)
        res.raise_for_status()
        data = res.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        current_code = current.get("weather_code", -1)
        current_icon, current_label = WEATHER_CODE_MAP.get(current_code, ("🌍", "Weather"))

        forecast = []
        dates = daily.get("time", [])
        mins = daily.get("temperature_2m_min", [])
        maxs = daily.get("temperature_2m_max", [])
        codes = daily.get("weather_code", [])

        for i in range(min(3, len(dates))):
            code = codes[i] if i < len(codes) else -1
            icon, label = WEATHER_CODE_MAP.get(code, ("🌍", "Weather"))
            forecast.append(
                {
                    "date": dates[i],
                    "icon": icon,
                    "label": label,
                    "min": mins[i] if i < len(mins) else "—",
                    "max": maxs[i] if i < len(maxs) else "—",
                }
            )

        return {
            "temperature": current.get("temperature_2m", "N/A"),
            "feels_like": current.get("apparent_temperature", "N/A"),
            "wind": current.get("wind_speed_10m", "N/A"),
            "icon": current_icon,
            "label": current_label,
            "forecast": forecast,
        }

    except Exception:
        return {
            "temperature": "N/A",
            "feels_like": "N/A",
            "wind": "N/A",
            "icon": "🌍",
            "label": "Unavailable",
            "forecast": [],
        }


# format forecast date label
def format_forecast_day(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%a")
    except Exception:
        return date_str
    
 
