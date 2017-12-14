from flask import Flask, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
import simplejson as json

from sqlalchemy.exc import IntegrityError

# DB model functions and classes
from model import createDB, setupDB, createTables   # Functions
from model import User                              # Classes
from model import app as application
from model import db


app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'


@app.route('/reset')
def createDatabase():
    HOSTNAME = 'mysqlserver'
    database = createDB(hostname=HOSTNAME)
    createTables()
    setupDB()
    return redirect(url_for('index'))


if __name__ == "__main__":
    context=('./app/self.vacation.crt','./app/self.vacation.key')
    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=context)