from flask import Flask, url_for, redirect, render_template, jsonify, session, request
#from flask_sqlalchemy import SQLAlchemy
from flask_appconfig import AppConfig
#import simplejson as json
from sqlalchemy.exc import IntegrityError, OperationalError

#from flask_wtf import FlaskForm
#from wtforms import StringField
#from wtforms.validators import DataRequired

# *************************************************
#              MAIN BACKEND PROGRAM
# *************************************************

# DB model functions and classes
from model import createDB, setupDB, createTables, hashID    # Functions
from model import ConfigData, User, Calendar, Holiday        # Classes
from model import app as application
from model import db

from form import RegistrationForm

from flask_oauth2_login import GoogleLogin


# Global debugging switch
# To start debugging in docker-compose, run the container the following way:
# docker-compose run --service-ports web
DEBUG_Flask = True
DEBUG = False

import pdb # XXX Should be excluded from final version


def appConfig():
    AppConfig(app, configfile=None)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False   # Suggested by SQLAlchemy

    # You must configure these 3 values from Google APIs console
    # https://code.google.com/apis/console          mateszedlak@invenshure.com
    app.config.update(
        SECRET_KEY = ConfigData.SECRET_KEY,
        GOOGLE_LOGIN_REDIRECT_SCHEME = ConfigData.GOOGLE_LOGIN_REDIRECT_SCHEME,
    )
    app.config["GOOGLE_LOGIN_CLIENT_ID"] = ConfigData.GOOGLE_LOGIN_CLIENT_ID
    app.config["GOOGLE_LOGIN_CLIENT_SECRET"] = ConfigData.GOOGLE_LOGIN_CLIENT_SECRET


# Initialize web app
app = Flask(__name__, static_url_path='/code/app/static')
appConfig()
google_login = GoogleLogin(app)


# ****************************************
#   MISSING PAGES:
# calendars, groups, users, profile
# ****************************************


@google_login.login_success
def login_success(token, profile):
    if DEBUG:
        pdb.set_trace()
    if (User.query.filter(User.ext_id == profile['id']).first() is not None):
        session['profile_ext_id_hashed'] = hashID(profile['id'])
        User.query.filter(User.ext_id == profile['id']).first().ext_id_hashed = session['profile_ext_id_hashed']
        db.session.commit()
        return redirect('home')
    else:
        session.clear()
        session['profile_name']=profile['name']
        session['profile_email']=profile['email']
        session['profile_picture']=profile['picture']
        session['profile_ext_id']=str(profile['id'])
        #session['profile_ext_id_hashed'] = hashID(profile['id'])
        return redirect('register')


@google_login.login_failure
def login_failure(e):
    try:
        session.clear()
    except Exception:
        pass
    return redirect(url_for('index'))


@app.route('/data')
def return_data():
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')

    #testdata = '[  {   "title": "New Year Eve",    "start": "2018-01-01"  },  {    "title": "Long Challenge",\n    "start": "2017-12-07",\n    "end": "2017-12-10"\n  },\n  {\n    "title": "Repeating Event",\n    "start": "2017-01-09T16:00:00-05:00"\n  },\n  {\n    "id": "999",\n    "title": "Repeating Event",\n    "start": "2017-01-16T16:00:00-05:00"\n  },\n  {\n    "title": "Codeforces",\n    "url": "http://codeforces.com/profile/sukeesh",\n    "start": "2017-01-11"\n  },\n  {\n    "title": "Meeting",\n    "start": "2017-01-12T10:30:00-05:00",\n    "end": "2017-01-12T12:30:00-05:00"\n  },\n  {\n    "title": "Lunch",\n    "start": "2017-01-12T12:00:00-05:00"\n  },\n  {\n    "title": "Meeting",\n    "start": "2017-01-12T14:30:00-05:00"\n  },\n  {\n    "title": "Happy Hour",\n    "start": "2017-01-12T17:30:00-05:00"\n  },\n  {\n    "title": "Dinner",\n    "start": "2017-01-12T20:00:00"\n  },\n  {\n    "title": "Birthday Party",\n    "start": "2017-01-13"\n  },\n  {\n    "title": "Github",\n    "url": "http://github.com/sukeesh",\n    "start": "2017-01-28"\n  }]'
    #return testdata
    user = User.query.filter(User.ext_id_hashed == session.get('profile_ext_id_hashed')).first()
    userid_filter = user.ext_id

    events = Holiday.query.filter((Holiday.user_id == userid_filter) &
                                  (~ (((Holiday.start < start_date) & (Holiday.end < start_date) & (Holiday.start < end_date) & (Holiday.end < end_date)) |
                                                                             ((Holiday.start > start_date) & (Holiday.end > start_date) & (Holiday.start > end_date) & (Holiday.end > end_date))))).all()
    events_arr = []
    for event in events:
        events_arr.append({
            'title': event.note | 'alma',
            'start': event.start.isoformat(),
            'end': event.end.isoformat()
        })
    return jsonify(events_arr)


@app.route('/')
def index():
    if DEBUG:
        pdb.set_trace()
    try:
        if (User.query.filter(User.ext_id_hashed==session.get('profile_ext_id_hashed')).first() is not None):
            return redirect('home')
        else:
            return render_template("landing.html", login_url=google_login.authorization_url())
    except OperationalError:
        return redirect("reset")
        # XXX Should be offered than to be default!


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        account_status = None
        account_type = None
        if not len(User.query.all()): # only active accounts shall be checked
            account_status = 1
            account_type = 2
        profile = User(name=session['profile_name'], nickname=form.nickname.data, ext_id=session['profile_ext_id'],
                       avatar_url=session['profile_picture'], email=session['profile_email'], birthday=form.birthday.data,
                       account_status=account_status, account_type = account_type)
        session['profile_ext_id_hashed'] = hashID(session['profile_ext_id'])
        session.pop('profile_ext_id')
        session.pop('profile_name')
        session.pop('profile_email')
        session.pop('profile_picture')
        try:
            db.session.add(profile)
            db.session.commit()
            return redirect('home')
        except KeyError:  # IntegrityError:
            db.session.rollback()
            session.clear()
            return redirect(url_for('index'))
        except IntegrityError:
            db.session.rollback()
            session.clear()
            return redirect(url_for('index'))

    return render_template('register.html', form=form)


@app.route('/home')
def home():
    # Standard conditions *************************************
    if DEBUG:
        pdb.set_trace()
    user = User.query.filter(User.ext_id_hashed==session.get('profile_ext_id_hashed')).first()
    if (user is None):
        session.clear()
        return redirect(url_for('index'))
    elif (user.account_status == 0):
        return render_template("message.html",
                               message="Please wait until admin approval. Contact an admin if needed.",
                               avatar_url=user.avatar_url)
    # End of standard conditions ******************************
    return render_template("home.html", avatar_url=user.avatar_url)


@app.route('/users')
def users():
    # Standard conditions *************************************
    if DEBUG:
        pdb.set_trace()
    user = User.query.filter(User.ext_id_hashed==session.get('profile_ext_id_hashed')).first()
    if (user is None):
        session.clear()
        return redirect(url_for('index'))
    elif (user.account_status == 0):
        return render_template("waitforapproval.html")
    elif (user.account_type != 2):
        return render_template("message.html", message="You do not have proper right to manage the user accounts. Please contact an admin if needed.", avatar_url=user.avatar_url)
    # End of standard conditions ******************************
    return render_template("message.html",
                        message="Hy!",
                        avatar_url=user.avatar_url)


@app.route('/logout')
def logout():
    try:
        session.clear()
    except Exception:
        pass
    return redirect("home")


@app.route('/reset')
def reset():
    database = createDB(hostname=ConfigData.HOSTNAME)
    createTables()
    setupDB()
    return redirect(url_for('index'))


if __name__ == "__main__":
    context=('./app/self.vacation.crt','./app/self.vacation.key')
    app.run(host="0.0.0.0", port=5000, debug=DEBUG_Flask, ssl_context=context)