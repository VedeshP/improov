import os

from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

import datetime

app = Flask(__name__)

# Set a secret key for the application
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# app.run(host='0.0.0.0') 

@app.route("/")
def flashing():
    flash("this is a test flash")
    return render_template("layout.html")
