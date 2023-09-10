from flask import Blueprint, render_template, request, url_for, redirect
from app import db
from flask_login import current_user, login_required
from userFunctions import checkUserPic, loadProfileData, getGoals
from workoutFunctions import getMax, dateList, totalWorkoutGraphs, makeGraph, exerciseList, statsGraph, getWorkoutData
from models import Userdata
profiles = Blueprint('profiles', __name__)

@profiles.route('/profile')
@login_required
def profile():

    Nums = [getMax('Squat (Barbell)'), getMax('Bench Press (Barbell)'), getMax('Deadlift (Barbell)')]

    return render_template('newProfile.html', picture=checkUserPic(), maxNums = Nums, userInfo = loadProfileData())

@profiles.route('/workouts')
@login_required
def workouts():
    user = Userdata.query.filter_by(email=current_user.email).first()
    
    if user.strongData:
        return render_template('workouts.html', name=current_user.name, picture=checkUserPic(), dates = dateList(), graph_json = totalWorkoutGraphs())
    else:
        Nums = [getMax('Squat (Barbell)'), getMax('Bench Press (Barbell)'), getMax('Deadlift (Barbell)')]
        return render_template('newProfile.html', picture=checkUserPic(), maxNums = Nums, userInfo = loadProfileData(), alert=True)
    

@profiles.route('/graphs')
@login_required
def graphs():
    user = Userdata.query.filter_by(email=current_user.email).first()
    
    if user.strongData:
        return render_template('graph.html', name=current_user.name,picture=checkUserPic(), exercises = exerciseList())
    else:
        Nums = [getMax('Squat (Barbell)'), getMax('Bench Press (Barbell)'), getMax('Deadlift (Barbell)')]
        return render_template('newProfile.html', picture=checkUserPic(), maxNums = Nums, userInfo = loadProfileData(), alert=True)
    
@profiles.route('/makeGraph', methods=['POST'])
@login_required
def loadGraph():
    exercise = request.form.get('exercise')
    graphType = request.form.get('GraphType')
    dateRange = request.form.get('dateRange')

    plot = makeGraph(exercise, dateRange, graphType)

    return render_template('graph.html', name=current_user.name,picture=checkUserPic(), graph = True, graph_json = plot)

@profiles.route('/stats')
@login_required
def stats():
    user = Userdata.query.filter_by(email=current_user.email).first()
    
    if user.strongData:
        Nums = [getMax('Squat (Barbell)'), getMax('Bench Press (Barbell)'), getMax('Deadlift (Barbell)')]
        graphs = [statsGraph('Squat (Barbell)'), statsGraph('Bench Press (Barbell)'), statsGraph('Deadlift (Barbell)')]
        return render_template('newStats.html', name=current_user.name,picture=checkUserPic(), maxNums = Nums, graph_json = graphs)
    else:
        Nums = [getMax('Squat (Barbell)'), getMax('Bench Press (Barbell)'), getMax('Deadlift (Barbell)')]
        return render_template('newProfile.html', picture=checkUserPic(), maxNums = Nums, userInfo = loadProfileData(), alert=True)

@profiles.route('/goals')
@login_required
def goals():
    return render_template('newGoals.html', name=current_user.name,picture=checkUserPic(), goalData = getGoals())

@profiles.route('/uploadStrong')
def uploadStrong():
  return render_template('profile.html', temp='setup.html', name=current_user.name, picture=checkUserPic())

@profiles.route('/selectWorkout', methods=['POST'])
def showWorkouts():
    #return getWorkoutData(request.form.get('workoutDate'))
    return render_template('workoutData.html', name=current_user.name,picture=checkUserPic(), workoutData = (getWorkoutData(request.form.get('workoutDate')))[0], workoutInfo = (getWorkoutData(request.form.get('workoutDate')))[1])
