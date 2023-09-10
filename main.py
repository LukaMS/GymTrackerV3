from flask import Blueprint, render_template
from app import db
from flask_login import login_required, current_user
from app import create_app
from models import Userinfo

main = Blueprint('main', __name__)

#route for homepage
@main.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('index.html', name=current_user.name)
    else:
        return render_template('index.html')

#route for homepage but with user name
@main.route('/index')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', name=current_user.name)
    else:
        return render_template('index.html')

app = create_app()
app.app_context().push()
db.create_all()