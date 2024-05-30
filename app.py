import os

from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from pyembed.core import PyEmbed

import datetime

from helpers import hello_world

app = Flask(__name__)
pyembed_instance = PyEmbed()

# Global variable to hold the text
#text = "Check out this cool video: https://www.youtube.com/watch?v=K8ZgwZf1E3E and https://youtube.com/shorts/orohA_db2OI?si=5z7gPgXEHcgmns98"
text = "this is the link for bootstrap https://getbootstrap.com/docs/5.3/forms/input-group/"

# Set a secret key for the application
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


# app.run(host='0.0.0.0') 

@app.route("/")
def index():
    
    return render_template("index.html", login=True)


@app.route("/know-more")
def know_more():
    ...


@app.route("/login")
def login():
    ...


@app.route("/signup")
def signup():
    ...


@app.route("/post")
def post():
    ...


@app.route("/communities")
def communities():
    ...


@app.route("/courses")
def courses():
    ...


@app.route("/blog")
def blog():
    ...


@app.route("/likes")
def likes():
    ...


@app.route("/bookmarks")
def bookmarks():
    ...


@app.route('/users/<username>')
def user_profile(username):
    return f'User profile page for {username}'

@app.route('/posts/<int:post_id>')
def post(post_id):
    return f'Viewing post with ID {post_id}'

@app.route('/replies/<int:reply_id>')
def reply(reply_id):
    return f'Viewing reply with ID {reply_id}'


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

@app.route("/testing")
def testing():
    urls = extract_urls(text)
    preview = generate_preview(urls[0]) if urls else None
    post = {
        'content': text,
        'preview': preview
    }
    return render_template('testing.html', post=post)