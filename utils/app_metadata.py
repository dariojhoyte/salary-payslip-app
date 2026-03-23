"""
App Metadata

purpose:
-Central place for descriptive information about the application, including versioning and author details
-

Dev notes:
- static data only (no caching required)
- accessed via helper getters across the app
"""

# --------------------------------------------------
# standard libraries
# --------------------------------------------------
# none

# --------------------------------------------------
# third-party libraries
# --------------------------------------------------
# none


# --------------------------------------------------
# application metadata
# --------------------------------------------------
def get_app_metadata():
    """
    Returns static metadata about the application.
    """
    return {
        "app": {
            "name": "Salary Payslip App",
            "icon": "🔐",
            "layout": "wide",
            "version": "1.0",
        },
        "author": {
            "name": "Dario J. Hoyte",
            "url": "www.dariohoyte.com",
        },
    }


# -----------------------------
# Convenience getters
# -----------------------------

def get_app_name():
    return get_app_metadata().get("app", {}).get("name", "App")


def get_app_icon():
    return get_app_metadata().get("app", {}).get("icon", "📄")


def get_app_layout():
    return get_app_metadata().get("app", {}).get("layout", "wide")


def get_app_version():
    return get_app_metadata().get("app", {}).get("version", "1.0")


def get_author_name():
    return get_app_metadata().get("author", {}).get("name", "Unknown Author")


def get_author_url():
    return get_app_metadata().get("author", {}).get("url", "")