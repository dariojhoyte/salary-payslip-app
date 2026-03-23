"""
Company configuration loader

purpose:
- loading company configuration from .json
- providing access to company-specifics (e.g name, logo etc.)

Dev notes:
- configuration cached using Streamlit cache for performance
- safe fallbacks provided for missing configuration values
- supports multi-company setup via company_key
"""

# --------------------------------------------------
# standard libraries
# --------------------------------------------------
from pathlib import Path
import json

# --------------------------------------------------
# third-party libraries
# --------------------------------------------------
import streamlit as st


# path to company configuration .json file
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "company_config.json"

# load and cache company configuration data
@st.cache_data
def load_company_config():
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"companies": {}}


# -----------------------------
# Core helper
# -----------------------------

def get_company(company_key: str):
    return load_company_config().get("companies", {}).get(company_key, {})



# -----------------------------
# Convenience getters
# -----------------------------

def get_company_name(company_key: str):
    return get_company(company_key).get("name", "Company")


def get_company_location(company_key: str):
    return get_company(company_key).get("location", "")


def get_company_logo(company_key: str):
    return get_company(company_key).get("logo", None)


def get_company_currency(company_key: str):
    return get_company(company_key).get("currency", "CAD")


def get_company_timezone(company_key: str):
    return get_company(company_key).get("timezone", "UTC")