import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError

import datetime

from helpers import login_required, apology, check_password_strength_basic, extract_urls, generate_preview, embed_link

app = Flask(__name__)


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
@login_required
def index():
    """Show home page with posts to the user"""
    if request.method == "GET":
        user_id = session["user_id"]

        rows = db.session.execute(
            text(
                """
                SELECT posts.*, users.username, users.display_name 
                FROM posts 
                JOIN users ON posts.user_id = users.id
                ORDER BY id DESC
                """
            )
        ).fetchall()

        # Convert each tuple to a list, modify it, and store in 'modified_rows'
        modified_rows = []
        for row in rows:
            row_list = list(row)
            if row_list[5]:
                row_list.append(embed_link(row_list[5]))
            else:
                row_list.append(None)
            modified_rows.append(tuple(row_list))
        #return jsonify(modified_rows)
        return render_template("index.html", login=True, show_taskbar = True, active_page = 'home', rows=modified_rows)


@app.route("/know-more")
def know_more():
    return render_template("know-more.html", show_taksbar = False)


@app.route("/login" , methods = ["GET","POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        password = request.form.get("password")
        if not username:
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not password:
            return apology("Must provide password", 403)
        
        # Query database for username
        rows = db.session.execute(
            text(
                "SELECT * FROM users WHERE username = :username"
            ), {"username" : username}
        ).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0][2], request.form.get("password") 
        ):
            return apology("invalid username and/or password", 403)
        
        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html", show_taskbar = False)


@app.route("/logout")
def logout():
    # Forget user
    session.clear()
    return redirect("/know-more")


@app.route("/signup", methods = ["GET", "POST"])
def signup():
    """Register user"""
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        
        username = request.form.get("username")
        username = username.strip().lower()
        display_name = request.form.get("display_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        birthday = request.form.get("birthday")

        for i in username:
            if i == ' ':
                return apology("username must not contain space", 400)
        if not username:
            return apology("Must provide username", 400)
        if not display_name:
            return apology("Must provide Display Name", 400)
        if not email:
            return apology("Please provide Email Id", 400)
        if not password:
            return apology("Please set a password", 400)
        if not confirm_password:
            return apology("Must confirm password", 400)
        if password != confirm_password:
            return apology("Both password must be same", 403)
        if not birthday:
            return apology("Please provide birthdate", 400)
        
        if check_password_strength_basic(password):
            return apology("Password must contain atleast 8 characters, a special character, letters and numbers", 403)
        
        hash = generate_password_hash(password)

        try:
            # Add user detials to the database
            # In place of password only hash is stored for safety and privacy
            db.session.execute(
                text(
                    "INSERT INTO users (username, password, display_name, date_of_birth, email_id) VALUES( :username, :hash, :display_name, :date_of_birth, :email_id)"
                ), {"username" : username, "hash" : hash, "display_name": display_name, "date_of_birth" : birthday, "email_id" : email}
            )
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            if "UNIQUE constraint failed: users.username" in str(e):
                return apology("Username already exists")
            elif "UNIQUE constraint failed: users.email_id" in str(e):
                return apology("Email ID already exists")
            else:
                return apology("An integrity error occurred")
        except Exception as e:
            db.session.rollback()
            return apology("An unexpected error occurred: " + str(e))
        

        flash("Signed Up! Login to proceed")
        return redirect("/login")
    else:
        return render_template("signup.html", show_taskbar = False)


@app.route("/post", methods = ["GET", "POST"])
@login_required
def post():
    """Let user post"""

    user_id = session["user_id"]

    rows = db.session.execute(
        text(
            "SELECT * FROM users WHERE id = :user_id"
        ), {"user_id" : user_id}
    ).fetchall()

    username = rows[0][1]
    display_name = rows[0][3]

    if request.method == "POST":
        primary_topic = request.form.get("primary_topic")
        internal_topic = request.form.get("internal_topic")
        post_content = request.form.get("post_content")
        link = request.form.get("link")

        created_at = datetime.datetime.now()
        
        if not primary_topic:
            return apology("Please provide primary/main topic", 403)
        if not internal_topic:
            return apology("Please provide internal/sub topic or set it to None", 403)
        if not post_content:
            return apology("Must write something in the post", 403)
        if not link:
            link = None

        db.session.execute(
            text(
                "INSERT INTO posts (user_id, content, main_topic, sub_topic, link, created_at) VALUES( :user_id, :content, :main_topic, :sub_topic, :link, :created_at)"
            ), {"user_id" : user_id, "content": post_content, "main_topic": primary_topic, "sub_topic": internal_topic, "link": link, "created_at": created_at}
        )
        db.session.commit()
        return redirect("/")
    
    else:
        return render_template("post.html", active_page = 'post', show_taskbar= True, username=username, display_name=display_name)


@app.route("/communities")
@login_required
def communities():
    return render_template("communites.html", show_taskbar = True, active_page = 'communities')


@app.route("/courses")
@login_required
def courses():
    return render_template("courses.html", active_page = 'courses')


@app.route("/blog")
@login_required
def blog():
    return render_template("blog.html", show_taskbar = True, active_page = 'blog')


@app.route("/likes", methods = ["GET", "POST"])
@login_required
def likes():
    if request.method == "GET":
        return render_template("index.html", active_page='likes')
    else:
        data = request.get_json()
        post_id = data['post_id']
        user_id = session["user_id"]

        try:
            db.session.execute(
                text(
                    "INSERT INTO likes (user_id, post_id) VALUES( :user_id, :post_id)"
                ), {"user_id": user_id, "post_id": post_id}
            )

            db.session.execute(
                text(
                    "UPDATE posts SET likes = likes + 1 WHERE id = :post_id"
                ), {"post_id": post_id}
            )

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            return apology("An unexpected error occurred: " + str(e))

        return jsonify({'success': True})


@app.route("/bookmarks", methods = ["GET", "POST"])
@login_required
def bookmarks():
    if request.method == "GET":
        return render_template("index.html", active_page = 'bookmarks')
    else: # Meaning POST method
        # learn about ajax here 
        data = request.get_json()
        post_id = data['post_id']
        user_id = session["user_id"]

        try:
            db.session.execute(
                text(
                    "INSERT INTO bookmarks (user_id, post_id) VALUES( :user_id, :post_id)"
                ), {"user_id": user_id, "post_id": post_id}
            )

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            return apology("An unexpected error occurred: " + str(e))
        
        return jsonify({'success': True})

        

@app.route('/users/<username>')
@login_required
def user_profile(username):
    return f'User profile page for {username}'

@app.route('/posts/<int:post_id>')
@login_required
def post_only(post_id):
    return f'Viewing post with ID {post_id}'

@app.route('/replies/<int:reply_id>')
@login_required
def reply(reply_id):
    return f'Viewing reply with ID {reply_id}'






# @app.route("/testing")
# def testing():
#     urls = extract_urls(text)
#     preview = generate_preview(urls[0]) if urls else None
#     post = {
#         'content': text,
#         'preview': preview
#     }
#     return render_template('testing.html', post=post)