from flask import Flask, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
import simplejson as json

from sqlalchemy.exc import IntegrityError

# DB model functions and classes
from model import CreateDB, SetUpDB     # Functions
from model import User                 # Classes
from model import app as application
from model import db


app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'


def createUserTable():
    try:
        db.create_all()
        return json.dumps({'status': True})
    except IntegrityError:
        db.session.rollback()
        return json.dumps({'status': False})


@app.route('/reset')
def createDatabase():
    HOSTNAME = 'mysqlserver'
    try:
        HOSTNAME = request.args['hostname']
    except:
        pass
    database = CreateDB(hostname='mysqlserver')
    createUserTable()
    return redirect(url_for('setup'))


@app.route('/setup')
def setup():
    SetUpDB()
    return redirect(url_for('index'))


if __name__ == "__main__":
    ssl_context=('./app/self.vacation.crt','./app/self.vacation.key')
    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=ssl_context)