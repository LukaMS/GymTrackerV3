from flask import Blueprint, redirect, url_for, request
from app import db
from flask_login import current_user
from google.cloud import storage
from models import Userinfo, Userdata, Usergoals
from workoutFunctions import updateGoalHistory

userFunctions = Blueprint('userFunctions', __name__)

def checkUserPic():

  if current_user.profilePic:
      return "https://storage.googleapis.com/silent-service-390716.appspot.com/profilePics/"+current_user.profilePic
  else:
      return 'https://storage.googleapis.com/silent-service-390716.appspot.com/profilePics/faviconLogo.png'

@userFunctions.route('/uploadData', methods=['POST'])
def uploadData():
    file = request.files['strongFile']
    filename = current_user.email+'STRONG.csv'

    storage_client = storage.Client()
    bucket = storage_client.bucket('silent-service-390716.appspot.com')
    blob = bucket.blob("StrongData/"+filename)
    blob.upload_from_file(file)

    user = Userdata.query.filter_by(email=current_user.email).first()
    if user:
        user.strongData = filename
    else:
        new_user = Userdata(email=current_user.email, strongData=filename)
        db.session.add(new_user)

    db.session.commit()

    return redirect(url_for('profiles.profile'))

def loadProfileData():
    user = Userdata.query.filter_by(email=current_user.email).first()
    if user:
        return [current_user.name, user.country, user.age, user.weight]
    else:
        new_user = Userdata(email=email,country='', age='', weight='')
        db.session.add(new_user)
        db.session.commit()
        return [current_user.name, user.country, user.age, user.weight]

def getGoals():
    user = Usergoals.query.filter_by(email=current_user.email).first()
    goalList = []
    if user.squatGoal:
        goalList.append(['Squat', user.squatGoal])
    else:
        goalList.append(['',''])
    if user.benchGoal:
        goalList.append(['Bench', user.benchGoal])
    else:
        goalList.append(['',''])
    if user.deadGoal:
        goalList.append(['Dead', user.deadGoal])
    else:
        goalList.append(['',''])
    if user.Goal3:
        goalList.append([user.Goal3Name, user.Goal3])
    else:
        goalList.append(['',''])
    if user.Goal4:
        goalList.append([user.Goal4Name, user.Goal4])
    else:
        goalList.append(['',''])
    if user.Goal5:
        goalList.append([user.Goal5Name, user.Goal5])
    else:
        goalList.append(['',''])
    return goalList

@userFunctions.route('/uploadGoal', methods=['POST'])
def uploadGoals():
    value = request.form.get('setGoal')
    goalType = request.form.get('goalType')
    user = Usergoals.query.filter_by(email=current_user.email).first()
    if goalType == 'squat':
        user.squatGoal = value
    elif goalType == 'bench':
        user.benchGoal = value
    elif goalType == 'dead':
        user.deadGoal = value
    elif goalType == 'goal1':
        exerciseName = request.form.get('exercise')
        user.Goal3 = value
        user.Goal3Name = exerciseName
    elif goalType == 'goal2':
        exerciseName = request.form.get('exercise')
        user.Goal4 = value
        user.Goal4Name = exerciseName
    elif goalType == 'goal3':
        exerciseName = request.form.get('exercise')
        user.Goal5 = value
        user.Goal5Name = exerciseName
    db.session.commit()
    updateGoalHistory(goalType, value)
    return redirect(url_for('profiles.goals'))

@userFunctions.route('/editProfileData', methods=['POST'])
def editProfileData():
    user = Userdata.query.filter_by(email=current_user.email).first()
    user.country = request.form.get('email')
    user.age = request.form.get('age')
    user.weight = request.form.get('weight')
    db.session.commit()

    return redirect(url_for('profiles.profile'))