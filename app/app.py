from flask import Flask, url_for, redirect, render_template, jsonify, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_appconfig import AppConfig
import simplejson as json
from sqlalchemy.exc import IntegrityError

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

# DB model functions and classes
from model import createDB, setupDB, createTables, hashID    # Functions
from model import User, Calendar                             # Classes
from model import app as application
from model import db

from form import RegistrationForm

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
        session['profile_name']=profile['name']
        session['profile_email']=profile['email']
        session['profile_picture']=profile['picture']
        session['profile_id']=profile['id']
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        account_status = None
        account_type = None
        if not len(User.query.all()):
            account_status = 1
            account_type = 2
        profile = User(name=session['profile_name'], nickname=form.nickname.data, ext_id=session['profile_id'],
                       avatar_url=session['profile_picture'], email=session['profile_email'], birthday=form.birthday.data,
                       account_status=account_status, account_type = account_type)
        session['profile_hashedID'] = hashID(session['profile_id'])
        session.pop('profile_name')
        session.pop('profile_email')
        session.pop('profile_picture')
        session.pop('profile_id')
        try:
            db.session.add(profile)
            db.session.commit()
        except KeyError:  # IntegrityError:
            db.session.rollback()
        except IntegrityError:
            db.session.rollback()

    return render_template('register.html', form=form)


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