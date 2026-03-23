# --------------------------------------------------
# standard libraries
# --------------------------------------------------
import os
import socket
from datetime import datetime, date, timezone

# --------------------------------------------------
# third-party libraries
# --------------------------------------------------
import streamlit as st

# --------------------------------------------------
# project modules
# --------------------------------------------------
from utils.company import get_company

from utils.auth import (
    load_auth_config, 
    verify_password, 
    init_session, 
    logout,)

from utils.helpers import (
    inject_base_styles,
    next_biweekly_dates,
    render_sidebar,
    get_user_location,
    get_weather,
    format_forecast_day,
)
from utils.app_metadata import (
    get_app_name,
    get_app_icon,
    get_app_layout,
    get_app_version,
)

# --------------------------------------------------
# page configuration
# --------------------------------------------------
# configure Streamlit page settings
st.set_page_config(
    page_title=get_app_name(),
    page_icon=get_app_icon(),
    layout=get_app_layout(),
)

# --------------------------------------------------
# UI helpers
# --------------------------------------------------
# hide sidebar and collapse control (used on login page)
def hide_sidebar():
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] { display: none; }
            [data-testid="collapsedControl"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# retrieve host machine name
def get_host_name():
    return (
        os.environ.get("COMPUTERNAME")
        or os.environ.get("HOSTNAME")
        or socket.gethostname()
        or "Unknown Host"
    )

# --------------------------------------------------
# login page
# --------------------------------------------------
# render login screen and handle authentication
def login_page():

    # apply app global styles 
    inject_base_styles()

    #hide sidebar
    hide_sidebar()

    # load authentication config and users
    config = load_auth_config()
    users = config.get("users", {})

    # load company configuration
    company_key = "air_barbados"
    st.session_state.company = get_company(company_key)
    company = st.session_state.get("company", {})

    # ensure users exist in config
    if not users:
        st.error("No users found in auth configuration.")
        return

    # map display names to usernames
    user_options = {
        user_data.get("name", username): username
        for username, user_data in users.items()
    }

    display_names = list(user_options.keys())

    # restore last selected user (if available)
    default_display_name = st.session_state.get("last_selected_user")
    default_index = 0
    if default_display_name in display_names:
        default_index = display_names.index(default_display_name)

    # render login header UI
    st.markdown(
        f"""
        <div class="login-title">
            <div class="login-badge">Secure Admin Access</div>
            <h1>Salary Payslip App</h1>
            <h2>{company.get('name', 'Company')}</h2>
            <p class="login-subtitle">
                Sign in to access payslip generation tools and help resources.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # centered login form layout
    with st.container():
        left, center, right = st.columns([1, 1.2, 1])
        with center:
            with st.form("login_form", clear_on_submit=False):

                st.markdown("### Sign In")

                # user selection dropdown
                selected_display_name = st.selectbox(
                    "Select User",
                    display_names,
                    index=default_index,
                )

                # password input field
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter password",
                )

                # button/action to submit login form
                submitted = st.form_submit_button("Login", use_container_width=True)

            # process login attempt
            if submitted:
                selected_username = user_options[selected_display_name]
                user = users.get(selected_username)

                if not user:
                    st.error("Invalid username or password.")
                    return

                # verify password (using PBKDF2)
                ok = verify_password(
                    password=password,
                    salt_hex=user.get("salt", ""),
                    stored_hash_hex=user.get("password_hash", ""),
                    iterations=int(user.get("iterations", 200000)),
                )

                if ok:
                    # initialize authenticated session
                    st.session_state.authenticated = True
                    st.session_state.username = selected_username
                    st.session_state.display_name = user.get("name", selected_username)
                    st.session_state.last_selected_user = selected_display_name
                    st.session_state.login_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                    st.session_state.host_name = get_host_name()
                    st.session_state.company_name = get_host_name()

                    st.rerun()
                else:
                    st.error("Invalid username or password.")

            st.caption("Authorized admin users only.")



# --------------------------------------------------
# Dashboard / Home Page
# --------------------------------------------------

# render main dashboard after authentication
def home_page():

    # apply app global styles 
    inject_base_styles()

    # render sidebar
    render_sidebar()

    # handle logout and redirect to login page
    if st.sidebar.button("Logout", use_container_width=True):
        logout()
        st.rerun()

    st.title("Dashboard")
    st.caption("Overview and quick access for payroll admins.")

    # retrieve data - dynamic and API calls
    today = date.today()
    payroll_dates = next_biweekly_dates(count=4)
    location = get_user_location()
    weather = get_weather(location["latitude"], location["longitude"])

    # --------------------------------------------------
    # top metrics (date, location, weather)
    # --------------------------------------------------
    c1, c2, c3 = st.columns(3)

    # current date
    with c1:
        st.markdown(
            f'''
            <div class="metric-card">
                <div class="metric-title">Today</div>
                <div class="metric-value">{today.strftime("%B %d, %Y")}</div>
                <div style="font-size:0.8rem; color:#4b5563;">
                    {today.strftime("%A")}
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

    # user location
    with c2:
        st.markdown(
            f'''
            <div class="metric-card">
                <div class="metric-title">Location</div>
                <div class="metric-value">{location["city"]}, {location["region"]}</div>
                <div style="font-size:0.8rem; color:#4b5563;">
                    {location["country_name"]}
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

    # weather summary and forecast
    with c3:
        forecast_html = ""

        # build forecast display
        for day in weather["forecast"]:
            forecast_html += f"""
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.82rem; margin-top:6px; padding-top:6px; border-top:1px solid rgba(0,0,0,0.06);">
                    <span>{format_forecast_day(day["date"])}</span>
                    <span>{day["icon"]} {day["max"]}° / {day["min"]}°</span>
                </div>
            """

        st.markdown(
            f'''
            <div class="metric-card">
                <div class="metric-title">Weather</div>
                <div class="metric-value">{weather["icon"]} {weather["temperature"]}°C</div>
                <div style="font-size:0.8rem; color:#4b5563;">
                    {weather["label"]}, Feels like: {weather["feels_like"]}°C • Wind: {weather["wind"]} km/h
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

    st.write("---")

    # --------------------------------------------------
    # payroll schedule and quick links
    # --------------------------------------------------
    left, right = st.columns(2)

    # payroll schedule section
    with left:
        st.subheader("Payroll Schedule")

        # next payroll date
        st.write(f"**Next payroll run:** {payroll_dates[0].strftime('%A, %B %d, %Y')}")

        # upcoming payroll dates list
        st.markdown(
            "<p style='margin-bottom:0;'><b>Upcoming biweekly payroll dates:</b></p>",
            unsafe_allow_html=True
        )
        for d in payroll_dates[1:]:
            st.markdown(
                f"<div>- {d.strftime('%B %d, %Y')}</div>",
                unsafe_allow_html=True,
            )

    # quick navigation links
    with right:
        st.subheader("Quick Links")

        st.page_link("pages/1_payslip_generator.py", label="Payslip Generator", icon="📄")
        st.page_link("pages/2_help.py", label="Help", icon="📘")


# --------------------------------------------------
# app entry point
# --------------------------------------------------
# initialize session and route user based on auth state
def main():
    init_session()

    if st.session_state.get("authenticated", False):
        home_page()
    else:
        login_page()

# run application
if __name__ == "__main__":
    main()