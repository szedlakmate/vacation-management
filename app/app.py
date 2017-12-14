from flask import Flask, url_for, redirect, render_template, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_appconfig import AppConfig
import simplejson as json

from sqlalchemy.exc import IntegrityError

# DB model functions and classes
from model import createDB, setupDB, createTables, hashID    # Functions
from model import User, Calendar                             # Classes
from model import app as application
from model import db

from flask_oauth2_login import GoogleLogin


def appConfig():
    AppConfig(app, configfile=None)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False   # Suggested by SQLAlchemy

    # You must configure these 3 values from Google APIs console
    # https://code.google.com/apis/console          mateszedlak@invenshure.com
    app.config.update(
        SECRET_KEY="secret",
        GOOGLE_LOGIN_REDIRECT_SCHEME="https",
    )
    app.config["GOOGLE_LOGIN_CLIENT_ID"] = '945161050960-9uafb16faeljklnvpu8gp31h5u23l517.apps.googleusercontent.com'
    app.config["GOOGLE_LOGIN_CLIENT_SECRET"] = 'qAH_V-G5Gx49uk1VmsoVioo4'


# Initialize webapp
app = Flask(__name__, static_url_path='/code/app/static')
appConfig()
google_login = GoogleLogin(app)


@google_login.login_success
def login_success(token, profile):
    if (session.get('hashedID') == hashID(profile['id'])):
        return redirect('home')
    else:
        session.clear()
        session['name']=profile['name']
        session['email']=profile['email']
        session['picture']=profile['picture']
        session['id']=profile['id']
        return redirect('register')


@google_login.login_failure
def login_failure(e):
    try:
        session.clear()
    except Exception:
        pass
    return redirect("index")


@app.route('/')
def index():
    return render_template("landing.html", login_url=google_login.authorization_url())


@app.route('/register')
def register():
    return render_template("landing.html", login_url=google_login.authorization_url())


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