from flask import Flask, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import simplejson as json

from sqlalchemy.exc import IntegrityError

# DB model functions and classes
from model import createDB, setupDB, createTables   # Functions
from model import User, Calendar                             # Classes
from model import app as application
from model import db


app = Flask(__name__, static_url_path='/code/app/static')

@app.route('/')
def index():
    return render_template("landing.html")


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