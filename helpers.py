from flask import redirect, render_template, request, session
from functools import wraps
import re


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/know-more")
        return f(*args, **kwargs)

    return decorated_function


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def check_password_strength_basic(password):
    if not re.search(r'[A-Za-z]', password):
        return True
    if not re.search(r'[0-9]', password):
        return True
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return True
    return False

# old code
# def check_password_strength_basic(password):
#         special_characters = '!@#$%^&*()-+?_=,<>/"'
#         if len(password) < 8:
#             return True
#         elif not any(c in special_characters for c in password):
#             return True
#         elif not any(c.isalnum() for c in password):
#             return True
#         return False