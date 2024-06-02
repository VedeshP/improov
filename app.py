import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from pyembed.core import PyEmbed

import datetime

from helpers import login_required

app = Flask(__name__)
pyembed_instance = PyEmbed()

# Global variable to hold the text
#text = "Check out this cool video: https://www.youtube.com/watch?v=K8ZgwZf1E3E and https://youtube.com/shorts/orohA_db2OI?si=5z7gPgXEHcgmns98"
#text = "this is the link for bootstrap https://getbootstrap.com/docs/5.3/forms/input-group/"

# Set a secret key for the application
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Get the current working directory
cwd = os.environ.get('CWD', os.getcwd())

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///improov.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# app.run(host='0.0.0.0') 


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET","POST"])
# @login_required
def index():
    if request.method == "POST":
        ...
    else:
        return render_template("index.html", login=True, show_taskbar = True, active_page = 'home')


@app.route("/know-more")
def know_more():
    render_template("know-more.html", show_taksbar = False)


@app.route("/login" , methods = ["GET","POST"])
def login():
    if request.method == "POST":
        ...
    else:
        return render_template("login.html", show_taskbar = False)


@app.route("/logout")
def logout():
    # Forget user
    session.clear()
    return redirect("/know-more")


@app.route("/signup", methods = ["GET", "POST"])
def signup():
    if request.method == "POST":
        ...
    else:
        return render_template("signup.html", show_taskbar = False)


@app.route("/post", methods = ["GET", "POST"])
# @login_required
def post():
    if request.method == "POST":
        ...
    else:
        return render_template("post.html", active_page = 'post', show_taskbar= True)


@app.route("/communities")
# @login_required
def communities():
    return render_template("communites.html", show_taskbar = True, active_page = 'communities')


@app.route("/courses")
# @login_required
def courses():
    return render_template("courses.html", active_page = 'courses')


@app.route("/blog")
# @login_required
def blog():
    return render_template("blog.html", show_taskbar = True, active_page = 'blog')


@app.route("/likes")
# @login_required
def likes():
    ...


@app.route("/bookmarks")
# @login_required
def bookmarks():
    ...


@app.route('/users/<username>')
# @login_required
def user_profile(username):
    return f'User profile page for {username}'

@app.route('/posts/<int:post_id>')
# @login_required
def post_only(post_id):
    return f'Viewing post with ID {post_id}'

@app.route('/replies/<int:reply_id>')
# @login_required
def reply(reply_id):
    return f'Viewing reply with ID {reply_id}'


# # Function to extract URLs from the text
# def extract_urls(text):
#     import re
#     url_pattern = re.compile(r'https?://\S+')
#     return url_pattern.findall(text)

# # Function to generate rich previews using PyEmbed
# def generate_preview(url):
#     try:
#         embed_html = pyembed_instance.embed(url)
#         if embed_html:
#             return {
#                 'url': url,
#                 'html': embed_html,
#                 'is_embed': True
#             }
#     except Exception as e:
#         print(f"Error embedding {url}: {e}")
#     return {
#         'url': url,
#         'html': f'<a href="{url}" target="_blank">{url}</a>',
#         'is_embed': False
#     }

# @app.route("/testing")
# def testing():
#     urls = extract_urls(text)
#     preview = generate_preview(urls[0]) if urls else None
#     post = {
#         'content': text,
#         'preview': preview
#     }
#     return render_template('testing.html', post=post)