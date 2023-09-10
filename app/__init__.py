from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from google.cloud.sql.connector import Connector

db = SQLAlchemy()


app = Flask(__name__, template_folder="../templates", static_folder = '../static')
def create_app():
    
    #setup secret key and sql(dont not touch sql unless completely broken)
    app.config['SECRET_KEY'] = '58edb3a2335f2499890062df97f8ee3c4d05a0f6e0e0ca76696ebc756f08107'

    #mysql+pymysql://lukams:Crosby231@/gymtracker-db?unix_socket=/cloudsql/silent-service-390716:northamerica-northeast2:gymtracker
    #mysql+pymysql://lukams:Crosby231@34.130.52.88/gymtracker-db

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://lukams:Crosby231@34.130.52.88/gymtracker-db'

    db.init_app(app)
    #load the login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    #create blueprints and what not
    from models import Userinfo

    @login_manager.user_loader
    def load_user(user_id):
        return Userinfo.query.get(int(user_id))
    
    from profiles import profiles as profiles_blueprint
    app.register_blueprint(profiles_blueprint)

    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from userFunctions import userFunctions as userFunctions_blueprint
    app.register_blueprint(userFunctions_blueprint)

    from workoutFunctions import workoutFunctions as workoutFunctions_blueprint
    app.register_blueprint(workoutFunctions_blueprint)

    return app


