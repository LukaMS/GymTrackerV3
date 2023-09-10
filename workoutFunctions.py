from flask import Blueprint, redirect, url_for, request
from app import db
from flask_login import current_user
from google.cloud import storage
from models import Userinfo, Userdata, Usergoals
import pandas as pd
from datetime import timedelta
import plotly.express as px
from plotly import utils
from json import dumps
import math
import fsspec
workoutFunctions = Blueprint('workoutFunctions', __name__)

def truncate(number, digits) -> float:
    # Improve accuracy with floating point operations, to avoid truncate(16.4, 2) = 16.39 or truncate(-1.13, 2) = -1.12
    nbDecimals = len(str(number).split('.')[1]) 
    if nbDecimals <= digits:
        return number
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

def getMax(exercise):
    user = Userdata.query.filter_by(email=current_user.email).first()
    if user.strongData:
      df = pd.read_csv("https://storage.googleapis.com/silent-service-390716.appspot.com/StrongData/"+user.strongData)
      Max = str(df.loc[df['Exercise Name'] == exercise].Weight.max())
      return Max
    else:
        return None
    
def dateList():
    user = Userdata.query.filter_by(email=current_user.email).first()
    if user.strongData:
      df = pd.read_csv("https://storage.googleapis.com/silent-service-390716.appspot.com/StrongData/"+user.strongData)
      unSplitDates = df.Date.unique().tolist()
      date_list = []

      for date in unSplitDates:
        new_date = date.split(' ')[0]
        date_list.append([new_date, date])
      return date_list
    else:
        return None

def exerciseList():
    user = Userdata.query.filter_by(email=current_user.email).first()
    if user.strongData:
      df = pd.read_csv("https://storage.googleapis.com/silent-service-390716.appspot.com/StrongData/"+user.strongData)
      exList = df['Exercise Name'].unique().tolist()
      exList.sort()
      return exList
    else:
        return None

def totalWorkoutGraphs():
  user = Userdata.query.filter_by(email=current_user.email).first()
  if user.strongData:
    
    date_list = dateList()

    start_date = (pd.Timestamp(date_list[0][0]))-timedelta(days = pd.Timestamp(date_list[0][0]).weekday())
    current_week = (pd.Timestamp(date_list[0][0])).isocalendar()[1]
    date_values = []
    weeks = 0
    day_count = 0

    for date in date_list:
        if pd.Timestamp(date[0]).isocalendar()[1] == current_week:
            day_count += 1
        elif pd.Timestamp(date[0]).isocalendar()[1] > current_week:
            date_values.append([(start_date+timedelta(days=7*weeks)), day_count])
            weeks += 1
            day_count = 1
            current_week = pd.Timestamp(date[0]).isocalendar()[1]
        elif pd.Timestamp(date[0]).isocalendar()[1] < current_week:
            date_values.append([(start_date+timedelta(days=7*weeks)), day_count])
            weeks += 1
            day_count = 1
            current_week = pd.Timestamp(date[0]).isocalendar()[1]

    df = pd.DataFrame(date_values, columns=['Date', 'Workouts'])

    fig = px.bar(df, x = 'Date',
                  y = 'Workouts',
                  title = 'Workouts Per Week', width=600, height=200, template="simple_white")
    fig.update_layout(margin=dict(l=0, r=20, t=40, b=20))
    fig.update_traces(marker_color='#d59eff')
    
    return dumps(fig, cls=utils.PlotlyJSONEncoder)
  else:
     return None

def makeGraph(exerciseName, dateRange, graphType):
  user = Userdata.query.filter_by(email=current_user.email).first()
  if user.strongData:
    df = pd.read_csv("https://storage.googleapis.com/silent-service-390716.appspot.com/StrongData/"+user.strongData)

    if graphType == 'Weight':
      sortedData = df.groupby(['Date', 'Exercise Name']).apply(lambda d: d.loc[d.Weight.idxmax()])
      locType = sortedData.loc[sortedData['Exercise Name'] == exerciseName].Weight
      indexed = locType.reset_index()
      graphData = indexed.drop(columns='Exercise Name')
    elif graphType == 'Reps':
      sortedData = df.groupby(['Date', 'Exercise Name']).apply(lambda d: d.loc[d.Reps.idxmax()])
      locType = sortedData.loc[sortedData['Exercise Name'] == exerciseName].Reps
      indexed = locType.reset_index()
      graphData = indexed.drop(columns='Exercise Name')
    elif graphType == 'Volume':
      df['Volume'] = df.Weight * df.Reps
      sortedData = df.groupby(['Date', 'Exercise Name']).apply(lambda d: d.loc[d.Volume.idxmax()])
      locType = sortedData.loc[sortedData['Exercise Name'] == exerciseName].Volume
      indexed = locType.reset_index()
      graphData = indexed.drop(columns='Exercise Name')

    fig = px.line(graphData, x = 'Date',
                  y = graphType,
                  title = exerciseName, width=800, height=300, markers=True, template='simple_white')
    fig.update_layout(margin=dict(l=0, r=20, t=40, b=20))
    fig.update_xaxes(showticklabels = False)
    fig.update_traces(marker_color='#d59eff', line_color='#d59eff')
    
    return dumps(fig, cls=utils.PlotlyJSONEncoder)

  else:
     return None

def statsGraph(exerciseName):
  user = Userdata.query.filter_by(email=current_user.email).first()
  if user.strongData:
    df = pd.read_csv("gs://silent-service-390716.appspot.com/StrongData/"+user.strongData)
    sortedData = df.groupby(['Date', 'Exercise Name']).apply(lambda d: d.loc[d.Weight.idxmax()])
    locType = sortedData.loc[sortedData['Exercise Name'] == exerciseName].Weight
    indexed = locType.reset_index()
    graphData = indexed.drop(columns='Exercise Name')

    Max = 0
    indexList = []
    
    for i in range(0, len(graphData)):
      if int(graphData.iloc[i,1]) > Max:
        Max = int(graphData.iloc[i,1])
      elif int(graphData.iloc[i,1]) <= Max:
        indexList.append(i)
    newData = graphData.drop(labels=indexList, axis=0)

    fig = px.line(newData, x = 'Date',
                  y = 'Weight',
                  title = exerciseName, width=225, height=200, markers=True, template='simple_white')
    fig.update_layout(margin=dict(l=0, r=20, t=40, b=20))
    fig.update_xaxes(showticklabels = False)
    fig.update_traces(marker_color='#d59eff', line_color='#d59eff')

    return dumps(fig, cls=utils.PlotlyJSONEncoder)

def updateGoalHistory(value, exerciseName):
  user = Userdata.query.filter_by(email=current_user.email).first()
  if user.goalData:
    df = pd.read_csv("https://storage.googleapis.com/silent-service-390716.appspot.com/goalHistory/"+user.goalData)
    newData = pd.DataFrame({'exercise':[exerciseName],'goalValue':[value],'complete':[0]})
    newdf = pd.concat([df, newData], ignore_index=True)

    storage_client = storage.Client()
    bucket = storage_client.bucket('silent-service-390716.appspot.com')
    blob = bucket.blob("goalHistory/"+user.goalData)
    blob.delete()
    bucket.blob('goalHistory/'+user.goalData).upload_from_string(newdf.to_csv(), 'text/csv')
  else:
    user.goalData = current_user.email+'GOALS'
    df = pd.DataFrame({'exercise': [exerciseName], 'goalValue': [value], 'complete':[0]})
    storage_client = storage.Client()
    bucket = storage_client.bucket('silent-service-390716.appspot.com')
    bucket.blob('goalHistory/'+user.goalData).upload_from_string(df.to_csv(index=False), 'text/csv')
    db.session.commit()

def getWorkoutData(date):
  user = Userdata.query.filter_by(email=current_user.email).first()
  df = pd.read_csv("https://storage.googleapis.com/silent-service-390716.appspot.com/StrongData/"+user.strongData)

  groupedData = df.loc[df.Date == date]
  numExercises = int(groupedData['Exercise Name'].unique().shape[0])

  dataList = [round(numExercises/2), numExercises]
  volumeList = []
  for i in range(0,numExercises):
    exercise = groupedData['Exercise Name'].unique()
    sets = groupedData.groupby(['Exercise Name'], sort = False )['Set Order'].max()
    exerciseData = groupedData.loc[groupedData['Exercise Name'] == exercise[i]]
    tempList = []
    tempList.append(exercise[i])
    tempList.append(int(sets[i]))
    for j in range(0, int(sets[i])):
      nums = exerciseData.iloc[j]
      setNum = j+1
      weight = truncate(float(nums.Weight), 2)
      reps = int(nums.Reps)
      volumeList.append(weight*reps)
      tempList.append([setNum, weight, reps])
    dataList.append(tempList)

  time = groupedData.Duration.unique()
  infoList = [date, time[0], numExercises, sum(volumeList)]

  return [dataList, infoList]   