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


def createTables():
    try:
        db.create_all()
    except IntegrityError:
        db.session.rollback()


@app.route('/reset')
def createDatabase():
    HOSTNAME = 'mysqlserver'
    database = CreateDB(hostname=HOSTNAME)
    createTables()
    SetUpDB()
    return redirect(url_for('index'))


if __name__ == "__main__":
    context=('./app/self.vacation.crt','./app/self.vacation.key')
    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=context)