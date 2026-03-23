"""
Authentication and session management

purpose:
- load user authentication configuration .json
- verify passwords using PBKDF2
- session state management
- enforcing access control across pages

Dev notes:
- passwords are stored as salted PBKDF2 hashes in auth_config.json
- security-sensitive operations (no caching used)
"""

# --------------------------------------------------
# standard libraries
# --------------------------------------------------
import json
import hashlib
from pathlib import Path

# --------------------------------------------------
# third-party libraries
# --------------------------------------------------
import streamlit as st


# path to authentication configuration .json file
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "auth_config.json"



# --------------------------------------------------
# Authentication Configurations
# --------------------------------------------------

# load authentication configurations from .json 
def load_auth_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# verify password using PBKDF2
def verify_password(password: str, salt_hex: str, stored_hash_hex: str, iterations: int = 200000) -> bool:
    #error handling
    try:
        # convert stored salt from hex to bytes
        salt = bytes.fromhex(salt_hex)

        # derive hash from input password
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        ).hex()

        # compare derived hash with stored hash
        return derived == stored_hash_hex

    #catch error
    except Exception:
        # return False on any failure (invalid input, decoding error, etc.)
        return False
    


# --------------------------------------------------
# Session Management
# --------------------------------------------------
# initialize default session state values
def init_session():
    defaults = {
        "authenticated": False,
        "username": None,
        "display_name": None,
        "last_selected_user": None,
        "login_time": None,
        "host_name": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# enforce authentication before accessing protected pages
def require_auth():

    init_session()

    if not st.session_state.get("authenticated", False):
        st.switch_page("main.py")

# clear session and preserve last selected user for convenience
def logout():
    last_selected_user = st.session_state.get("last_selected_user")

    # keys to remove from session state on logout
    keys_to_clear = [
        "authenticated",
        "username",
        "display_name",
        "login_time",
        "host_name",
        "company",
    ]

    # remove session keys safely
    for key in keys_to_clear:
        st.session_state.pop(key, None)

    # retain last selected user for next login
    st.session_state.last_selected_user = last_selected_user