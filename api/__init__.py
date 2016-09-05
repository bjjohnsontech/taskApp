from flask import Flask

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['TESTING'] = True
from api import routes