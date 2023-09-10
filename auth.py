from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from models import Userinfo, Userdata, Usergoals
from flask_login import login_user, login_required, logout_user, current_user
from google.cloud import storage
import sqlalchemy


auth = Blueprint('auth', __name__)

#check if user is logged in, if not then load the login form
@auth.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profiles.profile'))
    return render_template('login.html')

#catch the login request, verify credentials against the databases and then redirect to profile page
@auth.route('/login', methods=['POST'])
def login_post():
    if current_user.is_authenticated:
        return redirect(url_for('profiles.profile'))
    email = request.form.get('email')
    password = request.form.get('password')

    user = Userinfo.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return render_template('login.html', alert = True)

    login_user(user)
    return redirect(url_for('profiles.profile'))

#check if user is logged in, otherwise load the signup page
@auth.route('/signup')
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('profiles.profile'))
    return render_template('signup.html')

#cathch the signup request, verify the credentials with the data base and create a new user, then redirect to login
@auth.route('/signup', methods=['POST'])
def signup_post():
    if current_user.is_authenticated:
        return redirect(url_for('profiles.profile'))
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    conf_password = request.form.get('password-conf')

    if password != conf_password:
        return render_template('signup.html', passalert=True)

    user = Userinfo.query.filter_by(email=email).first()

    if user:
        return render_template('signup.html', emailalert=True)
    
    new_userInfo = Userinfo(email=email, name=name, password=generate_password_hash(password, method='sha256'))
    new_userData = Userdata(email=email,country='', age='', weight='')
    new_userGoals = Usergoals(email=email)

    db.session.add(new_userInfo)
    db.session.add(new_userData)
    db.session.add(new_userGoals)
    db.session.commit()

    return redirect(url_for('auth.login'))

#make sure the user is logged in, then log them out
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))