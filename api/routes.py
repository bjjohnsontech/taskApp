from flask import request
from api import app
from api.models import database as db, Task, Work
import json
from functools import wraps
from playhouse.shortcuts import model_to_dict, dict_to_model
import datetime
import re

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
    # will default to all if id, parent, and top are None
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
                # full days = 24 hours * 60 minutes + seconds divisible by 60, leave the remainder
            minutes = duration.days * 24 * 60 + (duration.seconds // 60)
            task['work_complete'] += minutes # add work minutes to this task
            task['work'].append(model_to_dict(work)) # add work row to list
        taskL.append(task)
        total_work += task['work_complete'] # track total time for this task for parent
    return {'total_work': total_work, 'tasks': taskL}


def time(ts):
    time_match = re.findall(r"([0-9.]+)([a-z]+)", ts, re.I)
    mins = 0
    if time_match:
        for amount, delim in time_match:
            if delim.lower() == 'd':
                # a day is only 8 hours
                mins += int(amount) * 8 * 60
            elif delim.lower() == 'h':
                mins += int(amount) * 60
            elif delim.lower() == 'm':
                mins += int(amount)
    return mins

@app.route('/task/', methods=['GET'])
@app.route('/task/<taskID>', methods=['GET'])
@databaseCon
def get_task(taskID=None):
    if taskID:
        if taskID == 'top':
            return json.dumps(get_tasks(top=True), default=json_serial)
        else:
            return json.dumps(get_tasks(id=taskID), default=json_serial)
    else:
        data = request.args
        if 'parent' in data:
            return json.dumps(get_tasks(parent=data['parent']), default=json_serial)
        else:
            return json.dumps(get_tasks(), default=json_serial)

@app.route('/task/', methods=['POST'])
@app.route('/task/<taskID>', methods=['PUT', 'DELETE'])
@databaseCon
def do_task(taskID=None):
    if taskID:
        if request.method == 'DELETE':
            task = Task.delete().where(Task.id == taskID)
            task.execute()
            return 'Success', 200
        elif request.method == 'PUT':
            data = request.args
            task = Task.select().where(Task.id == taskID)
            row = model_to_dict(task)
            # only change things that need changed
            if 'name' in data and data['name'] != row['name']:
                task.name = data['name']
            if 'description' in data and data['description'] != row['description']:
                task.description = data['description']
            if 'parent' in data and data['parent'] != row['parent']['id']:
                task.parent = data['parent']
            if 'completed' in data and data['completed'] != row['completed']:
                task.completed = data['completed']
            if 'block' in data and data['block'] != row['block']['id']:
                task.block = data['block']
            if 'label' in data and data['label'] != row['label']:
                task.label = data['label']
            if 'assigned' in data and data['assigned'] != row['assigned']:
                task.assigned = data['assigned']
            if 'estimate' in data:
                estimate = time(data['estimate'])
                if estimate != row['estimate']:
                    task.estimate = estimate
            task.save()
    else:
        data = request.get_json()
        task = Task(
            name = data.get('name', None),
            description = data.get('description', None),
            parent = data.get('parent', None) or None, # make sure None instead of ''
            completed = data.get('completed', None) or None, # make sure None instead of ''
            block = data.get('block', None) or None, # make sure None instead of ''
            label = data.get('label', None),
            assigned = data.get('assigned', None),
            estimate = time(data.get('estimate', '0m'))
        )
        task.save()
    return json.dumps(model_to_dict(task), default=json_serial)

@app.route('/work/', methods=['POST'])
@app.route('/work/<workID>', methods=['PUT', 'DELETE'])
@databaseCon
def do_work(workID=None):
    if workID:
        if request.method == 'DELETE':
            work = Work.delete().where(Work.id == workID)
            work.execute()
            return 'Success', 200
        elif request.method == 'PUT':
            data = request.get_json()
            work = Work.get(Work.id == workID)
            row = model_to_dict(work)
            start = data.get('start_time', None)
            if start and start != row['start_time']:
                start = datetime.datetime.strptime(start.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                work.start_time = start
            end = data.get('end_time', None)
            print end
            if end and end != row['end_time']:
                end = datetime.datetime.strptime(end.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                work.end_time = end
                print end
            work.save()
    else:
        data = request.get_json()
        start = data.get('start_time', None)
        if start:
            start = datetime.datetime.strptime(start.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        end = data.get('end_time', None)
        if end:
            end = datetime.datetime.strptime(end.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        work = Work(
            start_time = start,
            end_time = end,
            task = data.get('task', None) or None, # make sure None instead of ''
            user = 'bjohnson'#data.get('user', None) or None, # make sure None instead of ''
        )
        work.save()
    return json.dumps(model_to_dict(work), default=json_serial)