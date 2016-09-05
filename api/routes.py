from flask import render_template as rendTemp
from api import app
from api.models import database as db, Task, Work
import json
from functools import wraps
from playhouse.shortcuts import model_to_dict, dict_to_model
import datetime

def databaseCon(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db.connect()
        func = f(*args, **kwargs)
        db.close()
        return func
    return decorated_function

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")

@app.route('/')
@app.route('/index')
def index():
    return 'Hello World', 200

def get_tasks(id=None, parent=None, top=None):
    total_work = 0 # set total work to 0
    taskL = []
    tasks = Task.select()
    if id:
        tasks = tasks.select().where(Task.id == id)
    if parent:
        tasks = tasks.select().where(Task.parent == parent)
    elif top:
        tasks = tasks.where(Task.parent >> None)
    for task in tasks:
        task = model_to_dict(task)
        #print task
        children = get_tasks(parent=task['id'])
        child_work = children['total_work'] # track each task's children's work
        task['children'] = children['tasks'] # each task's children
        task['work'] = [] # list of dates task worked on
        task['work_complete'] = 0 + child_work # total amount of work done on this task + children
        for work in Work.select().where(Work.task == task['id']):
            if not work.end_time:
                duration = datetime.datetime.now() - work.start_time
            else:
                duration = work.end_time - work.start_time
            minutes = duration.days * 24 * 60 + (duration.seconds // 60)
            task['work_complete'] += minutes # add work minutes to this task
            task['work'].append(model_to_dict(work)) # add work row to list
        taskL.append(task)
        total_work += task['work_complete'] # track total time for this task for parent
    return {'total_work': total_work, 'tasks': taskL}

@app.route('/task/', methods=['GET'])
@app.route('/task/<taskID>', methods=['GET'])
@databaseCon
def get_task(taskID=None):
    if taskID:
        return json.dumps(get_tasks(id=taskID), default=json_serial)
    else:
        return json.dumps(get_tasks(top=True), default=json_serial)

@app.route('/pane_render.html')
def pane_render():
    return rendTemp('panes.html')