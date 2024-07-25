import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError

import datetime

from helpers import login_required, apology, check_password_strength_basic, embed_link, export_db, send_welcome_email

#from urllib.parse import urlparse, parse_qs

#import sqlitecloud

# #temporary code to check logs (testing)
# import logging

# # Configure logging
# logging.basicConfig(level=logging.DEBUG, filename='debug.log', filemode='w', 
#                     format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger()

app = Flask(__name__)

# Get the secret key from an environment variable
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


# Get the current working directory
cwd = os.environ.get('CWD', os.getcwd())

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



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

        # rows = db.session.execute(
        #     text(
        #         """
        #         SELECT posts.*, users.username, users.display_name 
        #         FROM posts 
        #         JOIN users ON posts.user_id = users.id
        #         ORDER BY id DESC
        #         """
        #     )
        # ).fetchall()

        rows = db.session.execute(
            text(
                """
                SELECT posts.*, 
                    users.username, 
                    users.display_name,
                    CASE WHEN likes.user_id IS NOT NULL THEN 1 ELSE 0 END AS liked,
                    CASE WHEN bookmarks.user_id IS NOT NULL THEN 1 ELSE 0 END AS bookmarked,
                    CASE WHEN follows.user_id IS NOT NULL THEN 1 ELSE 0 END AS followed
                FROM posts
                JOIN users ON posts.user_id = users.id
                LEFT JOIN likes ON posts.id = likes.post_id AND likes.user_id = :current_user_id
                LEFT JOIN bookmarks ON posts.id = bookmarks.post_id AND bookmarks.user_id = :current_user_id
                LEFT JOIN follows ON users.id = follows.following_user_id AND follows.user_id = :current_user_id
                ORDER BY posts.id DESC;
                """
            ), {"current_user_id": user_id}
        ).fetchall()

        # Convert each tuple to a list, modify it, and store in 'modified_rows'
        # modified_rows = []
        # for row in rows:
        #     row_list = list(row)
        #     if row_list[5]:
        #         row_list.append(embed_link(row_list[5]))
        #     else:
        #         row_list.append(None)
        #     modified_rows.append(tuple(row_list))
        modified_rows = [dict(row._mapping) for row in rows]        
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
        # Get details from the form
        username = request.form.get("username")
        username = username.strip()
        password = request.form.get("password")
        # Ensure username was submitted
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
    """Log User out"""
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
        username = username.strip()
        display_name = request.form.get("display_name")
        email = request.form.get("email")
        email = email.strip()
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
        
        # Get password hash to store in the database
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
        
        send_welcome_email(email, display_name)

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

        # Fetch iframe if link is provided
        iframe = None
        if link:
            preview = embed_link(link)
            if preview and 'preview' in preview and 'html' in preview['preview']:
                iframe = preview['preview']['html']

        try:
            db.session.execute(
                text(
                    "INSERT INTO posts (user_id, content, main_topic, sub_topic, link, created_at, iframe) VALUES( :user_id, :content, :main_topic, :sub_topic, :link, :created_at, :iframe)"
                ), {"user_id" : user_id, "content": post_content, "main_topic": primary_topic, "sub_topic": internal_topic, "link": link, "created_at": created_at, "iframe": iframe}
            )
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return apology("An unexpected error occurred: " + str(e))
        return redirect("/")
    
    else:
        topics = db.session.execute(
            text(
                "SELECT * FROM topics"
            )
        )
        return render_template("post.html", active_page = 'post', show_taskbar= True, username=username, display_name=display_name, topics=topics)


@app.route("/communities")
@login_required
def communities():
    # TODO: Make structure of how communites and messages will work
    return render_template("coming-soon.html", show_taskbar = True, active_page = 'communities')


@app.route("/courses")
@login_required
def courses():
    # TODO: Let user create and consume courses
    return render_template("coming-soon.html", active_page = 'courses', show_taskbar = True)


@app.route("/blog")
@login_required
def blog():
    # TODO: Let user post and read blogs and microblogs
    return render_template("coming-soon.html", show_taskbar = True, active_page = 'blog')


@app.route("/likes", methods = ["GET", "POST"])
@login_required
def likes():
    """Display user's likes"""
    if request.method == "GET":
        user_id = session["user_id"]
        rows = db.session.execute(
            text(
                """
                SELECT posts.*, 
                    users.username, 
                    users.display_name,
                    CASE WHEN bookmarks.user_id IS NOT NULL THEN 1 ELSE 0 END AS bookmarked,
                    CASE WHEN follows.user_id IS NOT NULL THEN 1 ELSE 0 END AS followed
                FROM posts
                JOIN users ON posts.user_id = users.id
                JOIN likes ON posts.id = likes.post_id AND likes.user_id = :current_user_id
                LEFT JOIN bookmarks ON posts.id = bookmarks.post_id AND bookmarks.user_id = :current_user_id
                LEFT JOIN follows ON users.id = follows.following_user_id AND follows.user_id = :current_user_id
                ORDER BY posts.id DESC;
                """
            ), {"current_user_id": user_id}
        ).fetchall()

                # Convert each tuple to a list, modify it, and store in 'modified_rows'
        # modified_rows = []
        # for row in rows:
        #     row_list = list(row)
        #     if row_list[5]:
        #         row_list.append(embed_link(row_list[5]))
        #     else:
        #         row_list.append(None)
        #     modified_rows.append(tuple(row_list))
         # New modified rows
        modified_rows = [dict(row._mapping) for row in rows]
        #return jsonify(modified_rows)
        return render_template("likes.html", active_page='likes', rows=modified_rows)
    else:
        """Register user's liked post (by json [JavaScript])"""
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


@app.route("/unlike", methods = ["POST"])
def unlike():
    if request.method == "POST":
        data = request.get_json()
        post_id = data["post_id"]
        user_id = session["user_id"]

        try:
            db.session.execute(
                text(
                    "DELETE FROM likes WHERE user_id = :user_id AND post_id = :post_id"
                ), {"user_id": user_id, "post_id": post_id}
            )

            db.session.execute(
                text(
                    "UPDATE posts SET likes = likes - 1 WHERE id = :post_id"
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
    """Display User's Bookmarks"""
    if request.method == "GET":
        user_id = session["user_id"]
        rows = db.session.execute(
            text(
                """
                SELECT posts.*, 
                    users.username, 
                    users.display_name,
                    CASE WHEN likes.user_id IS NOT NULL THEN 1 ELSE 0 END AS liked,
                    CASE WHEN follows.user_id IS NOT NULL THEN 1 ELSE 0 END AS followed
                FROM posts
                JOIN users ON posts.user_id = users.id
                JOIN bookmarks ON posts.id = bookmarks.post_id AND bookmarks.user_id = :current_user_id
                LEFT JOIN likes ON posts.id = likes.post_id AND likes.user_id = :current_user_id
                LEFT JOIN follows ON users.id = follows.following_user_id AND follows.user_id = :current_user_id
                ORDER BY posts.id DESC;
                """
            ), {"current_user_id": user_id}
        ).fetchall()

        # Convert each tuple to a list, modify it, and store in 'modified_rows'
        # modified_rows = []
        # for row in rows:
        #     row_list = list(row)
        #     if row_list[5]:
        #         row_list.append(embed_link(row_list[5]))
        #     else:
        #         row_list.append(None)
        #     modified_rows.append(tuple(row_list))
        # New modified rows
        modified_rows = [dict(row._mapping) for row in rows]
        #return jsonify(modified_rows)
        return render_template("bookmarks.html", active_page = 'bookmarks', rows=modified_rows)
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


@app.route("/unbookmark", methods = ["POST"])
def unbookmark():
    if request.method == "POST":
        data = request.get_json()
        post_id = data["post_id"]
        user_id = session["user_id"]

        try:
            db.session.execute(
                text(
                    "DELETE FROM bookmarks WHERE user_id = :user_id AND post_id = :post_id"
                ), {"user_id": user_id, "post_id": post_id}
            )

            db.session.commit()
        
        except Exception as e:
            db.session.rollback()
            return apology("An unexpected error occurred: " + str(e))
        
        return jsonify({'success': True})


@app.route("/follow", methods = ["POST"])
def follow():
    data = request.get_json()
    to_follow_user_id = data["user_id"]
    user_id = session["user_id"]

    try:
        db.session.execute(
            text(
                "INSERT INTO follows (user_id, following_user_id) VALUES( :user_id, :following_user_id)"
            ), {"user_id": user_id, "following_user_id": to_follow_user_id}
        )

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return apology("An unexpected error occurred: " + str(e))
    
    return jsonify({'success': True})


@app.route("/unfollow", methods = ["POST"])
def unfollow():
    data = request.get_json()
    to_unfollow_user_id = data["user_id"]
    user_id = session["user_id"]

    try:
        db.session.execute(
            text(
                "DELETE FROM follows WHERE user_id = :user_id AND following_user_id = :to_unfollow_user_id"
            ), {"user_id": user_id, "to_unfollow_user_id": to_unfollow_user_id}
        )

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return apology("An unexpected error occurred: " + str(e), 403)
    
    return jsonify({'success': True})


@app.route('/users/<username>/<int:display_user_id>', methods = ["GET", "POST"])
@login_required
def user_profile(username, display_user_id):
    """Display user info with followers and following"""
    user_id = session["user_id"]
    if request.method == "GET":

        following_check = db.session.execute(
            text(
                """
                SELECT * FROM follows WHERE 
                user_id = :user_id
                AND
                following_user_id = :display_user_id
                """
            ), {"user_id": user_id, "display_user_id": display_user_id}
        ).fetchall()

        follower_check = db.session.execute(
            text(
                """
                SELECT * FROM follows WHERE
                user_id = :display_user_id
                AND
                following_user_id = :user_id
                """
            ), {"user_id": user_id, "display_user_id": display_user_id}
        ).fetchall()

        display_name = db.session.execute(
            text(
                """
                SELECT display_name 
                FROM users 
                WHERE id = :display_user_id
                """
            ), {"display_user_id": display_user_id}
        ).fetchall()
        
        no_of_following = db.session.execute(
            text(
                """
                SELECT COUNT(*) AS following_count
                FROM follows
                WHERE user_id = :display_user_id
                """
            ), {"display_user_id": display_user_id}
        ).fetchall()

        no_of_followers = db.session.execute(
            text(
                """
                SELECT COUNT(*) AS follower_count
                FROM follows
                WHERE following_user_id = :display_user_id
                """
            ), {"display_user_id": display_user_id}
        ).fetchall()
        
        followings = db.session.execute(
            text(
                """
                SELECT follows.*,
                users.username
                FROM follows
                JOIN users ON follows.following_user_id = users.id
                WHERE follows.user_id = :display_user_id
                """
            ), {"display_user_id": display_user_id}
        ).fetchall()

        followers = db.session.execute(
            text(
                """
                SELECT follows.*,
                users.username
                FROM follows
                JOIN users ON follows.user_id = users.id
                WHERE follows.following_user_id = :display_user_id
                """
            ), {"display_user_id": display_user_id}
        ).fetchall()

        return render_template(
            "user-info.html",
            no_of_following=no_of_following, 
            no_of_followers=no_of_followers, 
            followers=followers, 
            followings=followings, 
            username=username, 
            display_name=display_name, 
            follower_check=follower_check, 
            following_check=following_check,
            display_user_id=display_user_id
            )


@app.route('/posts/<int:post_id>')
@login_required
def post_only(post_id):
    return f'Viewing post with ID {post_id}'

@app.route('/replies/<int:post_id>/<username>', methods = ["GET", "POST"])
@login_required
def reply(post_id, username):
    user_id = session["user_id"]
    if request.method == "POST":
        reply_content = request.form.get("reply_content")
        if not reply_content:
            return apology("Must provide a reply", 403)
        created_on = datetime.datetime.now()
        try:
            db.session.execute(
                text(
                    "INSERT INTO replies (post_id, user_id, reply, created_on) VALUES( :post_id, :user_id, :reply, :created_on)"
                ), {"post_id": post_id, "user_id": user_id, "reply": reply_content, "created_on": created_on}
            )

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            return apology("An unexpected error occurred: " + str(e), 403)
        
        return redirect(url_for('reply', post_id=post_id, username=username))

    else:
        replies = db.session.execute(
            text(
                """
                SELECT replies.*,
                users.username,
                users.display_name
                FROM replies
                JOIN users ON replies.user_id = users.id
                WHERE replies.post_id = :post_id
                ORDER BY id DESC
                """
            ), {"post_id": post_id}
        ).fetchall()

        return render_template("reply.html", replies=replies, username=username, post_id=post_id)
    

@app.route("/admin", methods = ["GET", "POST"])
def admin():
    if request.method == "GET":
        return render_template("admin.html")
    else:
        ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
        password = request.form.get("password")
        if not password:
            return apology("must provide password", 403)
        if password != ADMIN_PASSWORD:
            return apology("Invalid password", 403)
        return export_db()


@app.route("/add-topic", methods=["GET", "POST"])
def add_topic():
    if request.method == "POST":
        main_topic = request.form.get("primary_topic")
        sub_topic = request.form.get("sub_topic")
        try:

            db.session.execute(
                text(
                    "INSERT INTO topics(sub_topic, main_topic) VALUES( :sub_topic, :main_topic)"
                ), {"sub_topic": sub_topic, "main_topic":main_topic}
            )

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            return apology("An unexpected error occurred: " + str(e), 403)
        
        flash("Topic added")
        return redirect("/")
    else:
        return render_template("add-topic.html")


@app.route("/about-us")
def about_us():
    return render_template("about-us.html")


@app.route("/forgot-password", methods = ["GET", "POST"])
def change_password():
    if request.method == "POST":
        username = request.form.get("username")
        username = username.strip()
        email = request.form.get("email")
        date_of_birth = request.form.get("birthday")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username:
            return apology("Must provide Username", 403)
        if not date_of_birth:
            return apology("Must provide Birthday", 403)
        if not email:
            return apology("Must provide Email Id", 403)
        if not password:
            return apology("Please set a password", 400)
        if not confirm_password:
            return apology("Must confirm password", 400)
        if password != confirm_password:
            return apology("Both password must be same", 403)
        if check_password_strength_basic(password):
            return apology("Password must contain atleast 8 characters, a special character, letters and numbers", 403)


        rows = db.session.execute(
            text(
                """
                SELECT * FROM users 
                WHERE username = :username
                """
            ), {"username": username}
        ).fetchall()
        # Get a list of dictionaries (dictionary here) for easier retreiving of data
        modified_rows = [dict(row._mapping) for row in rows]

        if not modified_rows:
            return apology("Username not found", 403)

        # if check_password_hash(modified_rows["password"], password):
        #     return apology("")
        if modified_rows["email_id"] != email:
            return apology("Invalid Email", 403)
        if modified_rows["date_of_birth"] != date_of_birth:
            return apology("Invalid birthdate", 403)
        hash = generate_password_hash(password)

        try:
            db.session.execute(
                text(
                    """
                    UPDATE users
                    SET password = :hash 
                    WHERE username = :username
                    """
                ), {"hash": hash, "username": username}
            )
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return apology("An unexpected error occurred: " + str(e))
        #return jsonify(modified_rows)
        flash("password updated!")
        return redirect("/login")

    else: 
        return render_template("change-password.html")
        


# Test endpoint to check database connection and table existence
# @app.route('/test_connection')
# def test_connection():
#     try:
#         # List all tables in the database
#         tables_result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
#         tables = [row[0] for row in tables_result.fetchall()]

#         # Check if the 'users' table exists
#         if 'users' in tables:
#             # If the table exists, fetch its schema
#             schema_result = db.session.execute(text("PRAGMA table_info(users);"))
#             schema = [{'cid': row[0], 'name': row[1], 'type': row[2], 'notnull': row[3], 'dflt_value': row[4], 'pk': row[5]} for row in schema_result.fetchall()]
#             return jsonify({'message': 'Connected to database. Users table exists.', 'schema': schema})
#         else:
#             return jsonify({'message': 'Connected to database but users table does not exist.', 'tables': tables})
#     except Exception as e:
#         return jsonify({'error': str(e)})


# @app.route("/testing")
# def testing():
#     rows = db.session.execute(
#         text(
#             "SELECT * FROM posts"
#         )
#     ).fetchall()


#     modified_rows = [dict(row._mapping) for row in rows]
#     # Process each row to update iframe
#     # Process each row to update iframe
#     for row in modified_rows:
#         if row['link']:
#             preview = embed_link(row['link'])
            
#             # Log the preview content for debugging
#             logger.debug(f"Post ID: {row['id']}, Link: {row['link']}, Preview: {preview}")

#             # Check if the preview and nested keys exist
#             if preview and 'preview' in preview and 'html' in preview['preview']:
#                 row['iframe'] = preview['preview']['html']
#                 logger.debug(f"Post ID: {row['id']}, Generated iframe: {row['iframe']}")
#             else:
#                 logger.debug(f"Post ID: {row['id']}, Missing preview or HTML key")

#             # Update the database with the new iframe value
#             db.session.execute(
#                 text("UPDATE posts SET iframe = :iframe WHERE id = :id"),
#                 {"iframe": row['iframe'], "id": row['id']}
#             )

#     # Commit the changes to the database
#     db.session.commit()

#     # Return the JSON response
#     return jsonify(modified_rows)

