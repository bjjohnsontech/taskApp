from peewee import *
from config import user, password
database = MySQLDatabase('taskApp', **{'password': password, 'user': user})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Task(BaseModel):
    assigned = CharField(null=True)
    block = ForeignKeyField(db_column='block', null=True, rel_model='self', to_field='id')
    completed = DateTimeField(null=True)
    description = CharField()
    estimate = IntegerField(null=True)
    label = CharField(null=True)
    name = CharField()
    parent = ForeignKeyField(db_column='parent', null=True, rel_model='self', related_name='task_parent_set', to_field='id')

    class Meta:
        db_table = 'task'

class Work(BaseModel):
    end_time = DateTimeField()
    start_time = DateTimeField()
    task = ForeignKeyField(db_column='task_id', null=True, rel_model=Task, to_field='id')
    user = CharField(null=True)
    class Meta:
        db_table = 'work'

