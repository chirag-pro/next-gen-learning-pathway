"""
auth.py — User authentication with SHA-256 hashing and Streamlit session management.
"""

import hashlib
import json
import os
from datetime import datetime

import streamlit as st


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")


# ---------------------------------------------------------
# Password Hashing
# ---------------------------------------------------------

def hash_password(password):
    """Return SHA-256 hash of a password."""
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ---------------------------------------------------------
# Load Users
# ---------------------------------------------------------

def _load_users():
    """Load users from users.json."""

    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(USERS_FILE):
        return {}

    try:
        with open(
            USERS_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

            if isinstance(data, dict):
                return data

            return {}

    except (json.JSONDecodeError, OSError):
        return {}


# ---------------------------------------------------------
# Save Users
# ---------------------------------------------------------

def _save_users(users):
    """Save users to users.json."""

    os.makedirs(DATA_DIR, exist_ok=True)

    with open(
        USERS_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            users,
            f,
            indent=2,
            ensure_ascii=False
        )


# ---------------------------------------------------------
# Authenticate User
# ---------------------------------------------------------

def authenticate_user(username, password):
    """Check username and password."""

    username = username.strip()

    users = _load_users()

    if username not in users:
        return False

    stored_password = users[username].get("password")

    if not stored_password:
        return False

    return stored_password == hash_password(password)


# ---------------------------------------------------------
# Register User
# ---------------------------------------------------------

def register_user(username, password, email=""):
    """
    Register a new user.

    Returns:
        (True, success_message)
        or
        (False, error_message)
    """

    username = username.strip()
    email = email.strip()

    # Username validation
    if len(username) < 3:
        return False, "Username must be at least 3 characters."

    # Password validation
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    users = _load_users()

    # Existing username
    if username in users:
        return False, "Username already taken. Please choose another."

    # Create user
    users[username] = {
        "password": hash_password(password),
        "email": email,
        "created_at": datetime.now().isoformat(),
        "current_skill": None,
        "current_level": "Beginner",
    }

    _save_users(users)

    return True, "Account created successfully!"


# ---------------------------------------------------------
# Get User Information
# ---------------------------------------------------------

def get_user_info(username):
    """Return user information without password."""

    username = username.strip()

    users = _load_users()

    if username not in users:
        return {}

    info = dict(users[username])

    # Never expose password
    info.pop("password", None)

    return info


# ---------------------------------------------------------
# Update User Skill
# ---------------------------------------------------------

def update_user_skill(username, skill, level):
    """Update the user's selected skill and level."""

    users = _load_users()

    if username not in users:
        return False

    users[username]["current_skill"] = skill
    users[username]["current_level"] = level

    _save_users(users)

    return True


# ---------------------------------------------------------
# Login State
# ---------------------------------------------------------

def is_logged_in():
    """Return True if a user is currently logged in."""

    return bool(
        st.session_state.get("logged_in", False)
    )


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

def login(username):
    """Create Streamlit login session."""

    username = username.strip()

    st.session_state["logged_in"] = True
    st.session_state["username"] = username
    st.session_state["page"] = "dashboard"


# ---------------------------------------------------------
# Logout
# ---------------------------------------------------------

def logout():
    """Clear the current Streamlit session."""

    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Optional: force Streamlit to rerun
    st.rerun()