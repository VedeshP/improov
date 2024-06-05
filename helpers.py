from flask import redirect, render_template, request, session
from functools import wraps
import re
from pyembed.core import PyEmbed

pyembed_instance = PyEmbed()

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


# Function to extract URLs from the text
def extract_urls(text):
    import re
    url_pattern = re.compile(r'https?://\S+')
    return url_pattern.findall(text)


# Function to generate rich previews using PyEmbed
def generate_preview(url):
    try:
        embed_html = pyembed_instance.embed(url)
        if embed_html:
            return {
                'url': url,
                'html': embed_html,
                'is_embed': True
            }
    except Exception as e:
        print(f"Error embedding {url}: {e}")
    return {
        'url': url,
        'html': f'<a href="{url}" target="_blank">{url}</a>',
        'is_embed': False
    }


def embed_link(link_text):
    urls = extract_urls(link_text)
    preview = generate_preview(urls[0]) if urls else None
    post = {
        'content': link_text,
        'preview': preview
    }
    return post



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