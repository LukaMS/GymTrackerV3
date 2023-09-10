from app import db
from flask_login import UserMixin

#user model that needs some updates but i think it will be a pain in the ass so its delayed
class Userinfo(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    profilePic = db.Column(db.String(1000))   

class Userdata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    strongData = db.Column(db.String(1000))
    goalData = db.Column(db.String(1000))
    country = db.Column(db.String(1000))
    age = db.Column(db.String(1000))
    weight = db.Column(db.String(1000))
    
class Usergoals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    squatGoal = db.Column(db.String(1000))
    benchGoal = db.Column(db.String(1000))
    deadGoal = db.Column(db.String(1000))
    Goal5Name = db.Column(db.String(1000))
    Goal5 = db.Column(db.String(1000))
    Goal4Name = db.Column(db.String(1000))
    Goal4 = db.Column(db.String(1000))
    Goal3Name = db.Column(db.String(1000))
    Goal3 = db.Column(db.String(1000))