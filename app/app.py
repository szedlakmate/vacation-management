from datetime import timedelta
from flask import Flask, url_for, redirect, render_template, jsonify, session, request
from flask_mail import Mail, Message
#from flask_sqlalchemy import SQLAlchemy
from flask_appconfig import AppConfig
#import simplejson as json
from sqlalchemy.exc import IntegrityError, OperationalError


# *************************************************
#              MAIN BACKEND PROGRAM
# *************************************************

# DB model functions and classes
from model import createDB, setupDB, createTables, hashID                   # Functions
from model import User, Calendar, Holiday, GroupMember, Group   # Classes
from model import app as application
from model import db

from config import ConfigData           # Configuration

from form import RegistrationForm, NewEventForm

from flask_oauth2_login import GoogleLogin


# Global debugging switch
# To start debugging in docker-compose, run the container the following way:
# docker-compose run --service-ports web
DEBUG_FLASK = ConfigData.DEBUG_FLASK
DEBUG = ConfigData.DEBUG

if DEBUG:
    import pdb

def appConfig():
    AppConfig(app, configfile=None)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False   # Suggested by SQLAlchemy

    app.config.update(
        SECRET_KEY = ConfigData.GOOGLE_SECRET_KEY,
        GOOGLE_LOGIN_REDIRECT_SCHEME = ConfigData.GOOGLE_LOGIN_REDIRECT_SCHEME,
    )
    app.config["GOOGLE_LOGIN_CLIENT_ID"] = ConfigData.GOOGLE_LOGIN_CLIENT_ID
    app.config["GOOGLE_LOGIN_CLIENT_SECRET"] = ConfigData.GOOGLE_LOGIN_CLIENT_SECRET
    app.config["MAIL_SERVER"] = ConfigData.MAIL_SERVER
    app.config["MAIL_PORT"] = ConfigData.MAIL_PORT
    app.config["MAIL_USE_SSL"] = ConfigData.MAIL_USE_SSL
    app.config["MAIL_USE_TLS"] = ConfigData.MAIL_USE_TLS
    app.config["MAIL_USERNAME"] = ConfigData.MAIL_USERNAME
    app.config["MAIL_PASSWORD"] = ConfigData.MAIL_PASSWORD
    app.config["MAIL_DEFAULT_SENDER"] = ConfigData.MAIL_DEFAULT_SENDER


# Initialize web app
app = Flask(__name__, static_url_path='/code/app/static')
appConfig()
google_login = GoogleLogin(app)
mail = Mail()
mail.init_app(app)


@google_login.login_success
def login_success(token, profile):
    if DEBUG:
        pdb.set_trace()
    if User.query.filter(User.ext_id == profile['id']).first() is not None:
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
        return redirect('register')


@google_login.login_failure
def login_failure(e):
    try:
        session.clear()
    except Exception:
        pass
    return redirect(url_for('index'))


def getevents(start_date, end_date, user, get_all):
    all_events = Holiday.query.filter((~ (((Holiday.start < start_date) & (Holiday.end < start_date) & (Holiday.start < end_date) & (Holiday.end < end_date)) |
                                                                             ((Holiday.start > start_date) & (Holiday.end > start_date) & (Holiday.start > end_date) & (Holiday.end > end_date)))))
    if user.account_type > 0 and get_all:
        events = all_events.all()
    else:
        events = all_events.filter(Holiday.user_id == user.ext_id).all()
    return events


# Query for Holiday events
@app.route('/data')
def return_data():
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    user = User.query.filter(User.ext_id_hashed == session.get('profile_ext_id_hashed')).first()
    get_all = True
    events = getevents(start_date, end_date, user, get_all)
    events_arr = []
    for event in events:
        event_color = ''
        style = ''
        if event.status == 0:
            style += 'redborder'
        elif event.status == -1:
            style += 'light'
        if event.user_id == user.ext_id:
            event_color += 'default'
        else:
            event_color += ConfigData.CAL_COLORMAP[int((User.query.filter(User.ext_id == event.user_id).first().ext_id_hashed)) % len(ConfigData.CAL_COLORMAP)]
        if style and event_color:
            style += " "
        if event_color:
            style += event_color
        title = ''
        if event.user_id:
            if user.account_type > 0:
                title += str(User.query.filter(User.ext_id == event.user_id).first().nickname)
            else:
                title += str(Calendar.query.filter(Calendar.id == event.calendar_id).first().name)
        if event.note:
            title += '-' + event.note
        events_arr.append({
            'title': title,
            'url': event.url,
            'start': event.start.isoformat(),
            'end': (event.end + timedelta(days=1)).isoformat(),
            'style': style
        })
    return jsonify(events_arr)

# Query for Holiday events
@app.route('/activateuser', methods=['GET', 'POST'])
def activateuser():
    if DEBUG:
        pdb.set_trace()
    user_id = request.form.get('id', '')
    action = request.form.get('action', '')
    typechange = request.form.get ('typechange','')
    if not user_id:
        user_id = typechange
    if action is None:
        action = 1
    else:
        try:
            action = int(action)
        except Exception:
            pass
    try:
        user = User.query.filter(User.ext_id == user_id).first()
        if not typechange:
            user.account_status = action
            if action == 1:

                msg = Message("Account activation",
                              sender="noreply@example.com",
                              recipients=[user.email])
                msg.body = "Dear %s,\n\nYour Vacation Management account is now active.\n\nBest regards,\nThe VM Team" % user.nickname
                mail.send(msg)
        else:
            user.account_type = (user.account_type + 1) % 3
        db.session.commit()
    except KeyError:
        db.session.rollback()
        return redirect("users")
    except IntegrityError:
        db.session.rollback()
    return redirect("users")

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
    if (request.method == 'POST' and form.validate() and form.post_validate()):
        account_status = None
        account_type = None
        if not len(User.query.filter(User.account_status == 1).all()):
            account_status = 1
            account_type = 2
        profile = User(name=session['profile_name'],
                       nickname=form.nickname.data,
                       ext_id=session['profile_ext_id'],
                       avatar_url=session['profile_picture'],
                       email=session['profile_email'],
                       birthday=form.birthday.data,
                       account_status=account_status,
                       account_type = account_type)
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
                               message="Please wait for admin approval. Contact an admin if needed.",
                               avatar_url=user.avatar_url)
    # End of standard conditions ******************************
    return render_template("home.html", user=user)


@app.route('/newevent', methods=['GET', 'POST'])
def newevent():
    # Standard conditions *************************************
    if DEBUG:
        pdb.set_trace()
    user = User.query.filter(User.ext_id_hashed==session.get('profile_ext_id_hashed')).first()
    if (user is None):
        session.clear()
        return redirect(url_for('index'))
    elif (user.account_status == 0):
        return render_template("message.html",
                               message="Please wait for admin approval. Contact an admin if needed.",
                               avatar_url=user.avatar_url)
    # End of standard conditions ******************************
    form = NewEventForm(request.form)
    if request.method == 'POST' and form.validate():
        calendar_id=form.calendar_list.data.id
        start = form.start.data
        end = form.end.data
        note = form.note.data
        event = Holiday(user_id=user.ext_id,
                        calendar_id=calendar_id,
                        url='',
                        start=start,
                        end=end,
                        note=note)
        try:
            db.session.add(event)
            db.session.commit()
            try:
                if DEBUG:
                    pdb.set_trace()
                event = Holiday.query.filter((Holiday.user_id == user.ext_id) &
                                             (Holiday.calendar_id == calendar_id) &
                                             (Holiday.start == start) &
                                             (Holiday.end == end)).first()
                event.url = '/event/' + str(event.id)
                db.session.commit()
            except AttributeError:
                db.session.rollback()
                #return redirect(url_for('home'))
            return redirect(url_for('home'))
        except KeyError:  # IntegrityError:
            db.session.rollback()
            return redirect(url_for('home'))
        except IntegrityError:
            db.session.rollback()
            return redirect(url_for('home'))


    return render_template('newevent.html', form=form, user=user)


@app.route('/users')
def users():
    # Conditions *************************************
    if DEBUG:
        pdb.set_trace()
    user = User.query.filter(User.ext_id_hashed==session.get('profile_ext_id_hashed')).first()
    if (user is None):
        session.clear()
        return redirect(url_for('index'))
    elif (user.account_status == 0):
        return render_template("message.html",
                               message="Please wait for admin approval. Contact an admin if needed.",
                               avatar_url=user.avatar_url)
    elif (user.account_type != 2):
        return render_template("message.html", message="You do not have proper right to manage the user accounts. Please contact an admin if needed.", avatar_url=user.avatar_url)
    # End of conditions ******************************
    if DEBUG:
        pdb.set_trace()
    inactive = User.query.filter(User.account_status == 0).all()
    active = User.query.filter((User.account_status == 1)).all()
    current_ext_id = user.ext_id
    return render_template("users.html",
                        user=user, inactive=inactive, active=active, current_ext_id=current_ext_id)


@app.route('/event/<event_id>', methods=['GET', 'POST'])
def eventedit(event_id):
    # Conditions *************************************
    if DEBUG:
        pdb.set_trace()
    user = User.query.filter(User.ext_id_hashed==session.get('profile_ext_id_hashed')).first()
    event = Holiday.query.filter(Holiday.id == event_id).first()
    try:
        if (user is None):
            session.clear()
            return redirect(url_for('index'))
        elif (user.account_status == 0):
            return render_template("message.html",
                                   message="Please wait for admin approval. Contact an admin if needed.",
                                   avatar_url=user.avatar_url)
        elif (user.account_type < 1) and (event.user_id != user.ext_id) and (event.status != 0):
            return render_template("message.html", message="You cannot edit this holiday.", avatar_url=user.avatar_url)
    except AttributeError:
        return render_template("message.html", message="You cannot edit this holiday.", avatar_url=user.avatar_url)
    # End of conditions ******************************
    if DEBUG:
        pdb.set_trace()

    event_user = User.query.filter(User.ext_id == event.user_id).first()

    if not event.note:
        note = ""
    else:
        note = event.note

    event_allow = None
    try:
        event_allow = int(request.form.get('allow', ''))
    except ValueError:
        event_allow = None
    if event_allow:
        if event_allow == -1 or event_allow == 1:
            event.status = event_allow
        if event_allow == -2:
            db.session.delete(event)
        try:
            db.session.commit()
            return redirect('home')
        except Exception:
            db.session.rollback()


    return render_template("eventedit.html",
                           user=user,
                           account_type=user.account_type,
                           username=event_user.nickname,
                           calendar_name=Calendar.query.filter(Calendar.id == event.calendar_id).first().name,
                           start=event.start,
                           end=event.end,
                           note=note,
                           status=event.status
                           )


@app.route('/profile')
def profile():
    # Conditions *************************************
    if DEBUG:
        pdb.set_trace()
    user = User.query.filter(User.ext_id_hashed==session.get('profile_ext_id_hashed')).first()
    if (user is None):
        session.clear()
        return redirect(url_for('index'))
    elif (user.account_status == 0):
        return render_template("message.html",
                               message="Please wait for admin approval. Contact an admin if needed.",
                               avatar_url=user.avatar_url)
    # End of conditions ******************************
    group_ids = GroupMember.query.filter(GroupMember.user_id == user.ext_id).all()
    group_names = []
    if group_ids:
        for group in group_ids:
            group_names.append(Group.query.filter(Group.id == group.group_id).first())
    account_type = ""
    account_status = ""

    if user.account_type == 0:
        account_type = "Standard user"
    elif user.account_type == 1:
        account_type = "Viewer"
    elif user.account_type == 2:
        account_type = "Admin"

    if user.account_status == 0:
        account_status = "Not activated"
    elif user.account_status == 1:
        account_status = "Active"
    elif user.account_status == -1:
        account_status = "Deactivated"

    return render_template("profile.html", avatar_url=user.avatar_url, user=user, groups=group_names, account_type=account_type, account_status=account_status)


@app.route('/groups')
def groups():
    # Conditions *************************************
    if DEBUG:
        pdb.set_trace()
    user = User.query.filter(User.ext_id_hashed==session.get('profile_ext_id_hashed')).first()
    if user is None:
        session.clear()
        return redirect(url_for('index'))
    elif user.account_status == 0:
        return render_template("message.html",
                               message="Please wait for admin approval. Contact an admin if needed.",
                               avatar_url=user.avatar_url)
    elif user.account_type != 2:
        return render_template("message.html", message="You do not have proper right to access this site. Please contact an admin if needed.", avatar_url=user.avatar_url)
    # End of conditions ******************************

    groups = Group.query.all()
    return render_template("groups.html", avatar_url=user.avatar_url, groups=groups, user=user)


@app.route('/groups/<id>', methods=['GET', 'POST'])
def group_edit(id):
    # Conditions *************************************
    if DEBUG:
        pdb.set_trace()
    user = User.query.filter(User.ext_id_hashed==session.get('profile_ext_id_hashed')).first()
    if user is None:
        session.clear()
        return redirect(url_for('index'))
    elif user.account_status == 0:
        return render_template("message.html",
                               message="Please wait for admin approval. Contact an admin if needed.",
                               avatar_url=user.avatar_url)
    elif user.account_type != 2:
        return render_template("message.html", message="You do not have proper right to access this site. Please contact an admin if needed.", avatar_url=user.avatar_url)
    # End of conditions ******************************
    group = Group.query.filter(Group.id == id).first()
    if not group:
        return redirect('/groups')
    else:
        member = []
        outer = []
        for account in User.query.all():
            if GroupMember.query.filter(GroupMember.group_id == id, GroupMember.user_id == account.ext_id).all():
                member.append(account)
            else:
                outer.append(account)
        # member.sort()
        # outer.sort()
        return render_template('newgroup.html', user=user, group=group, member=member, outer=outer)


@app.route('/newgroup', methods=['GET', 'POST'])
def newgroup():
    # Conditions *************************************
    if DEBUG:
        pdb.set_trace()
    user = User.query.filter(User.ext_id_hashed==session.get('profile_ext_id_hashed')).first()
    if user is None:
        session.clear()
        return redirect(url_for('index'))
    elif user.account_status == 0:
        return render_template("message.html",
                               message="Please wait for admin approval. Contact an admin if needed.",
                               avatar_url=user.avatar_url)
    elif user.account_type != 2:
        return render_template("message.html", message="You do not have proper right to access this site. Please contact an admin if needed.", avatar_url=user.avatar_url)
    # End of conditions ******************************
    group_action = request.values.get('group_action', '')
    user_action = request.values.get('user_action', '')
    if group_action:
        new_name = request.values.get('new_name', '')
        group_id = request.values.get('group_id', '')
        if group_action == "add":
            try:
                group = Group(name=new_name)
                db.session.add(group)
                db.session.commit()
            except Exception:
                db.session.rollback()
        if group_action == "rename":
            try:
                group = Group.query.filter(Group.id == group_id).first()
                group.name = new_name
                db.session.commit()
            except Exception:
                db.session.rollback()
        elif group_action == "cancel":
            return redirect("/groups")
        elif group_action == "delete":
            try:
                group = Group.query.filter(Group.id == group_id).first()
                member_data = GroupMember.query.filter(GroupMember.group_id == group_id).all()
                db.session.delete(group)
                for member in member_data:
                    db.session.delete(member)
                db.session.commit()
            except Exception:
                db.session.rollback()
        return redirect('/groups')
    if user_action:
        user_id = request.values.get('user_id', '')
        group_id = request.values.get('group_id', '')
        if user_action == "add":
            try:
                new_member = GroupMember(group_id=group_id, user_id=user_id)
                db.session.add(new_member)
                db.session.commit()
            except Exception:
                db.session.rollback()
        elif user_action == "remove":
            try:
                old_member = GroupMember.query.filter(GroupMember.user_id == user_id, GroupMember.group_id == group_id).first()
                db.session.delete(old_member)
                db.session.commit()
            except Exception:
                db.session.rollback()
        if len(str(group_id)) > 0:
            return redirect('/groups/' + str(group_id))
        else:
            return redirect('/groups')
    return render_template('newgroup.html', user=user, group=None, member=[], outer=User.query.all())


@app.route('/calendars', methods=['GET', 'POST'])
def calendars():
    # Conditions *************************************
    if DEBUG:
        pdb.set_trace()
    user = User.query.filter(User.ext_id_hashed==session.get('profile_ext_id_hashed')).first()
    if (user is None):
        session.clear()
        return redirect(url_for('index'))
    elif (user.account_status == 0):
        return render_template("message.html",
                               message="Please wait for admin approval. Contact an admin if needed.",
                               avatar_url=user.avatar_url)
    elif (user.account_type != 2):
        return render_template("message.html", message="You do not have proper right to access this site. Please contact an admin if needed.", avatar_url=user.avatar_url)
    # End of conditions ******************************
    calendar_id = request.values.get('calendar_id', '')
    if calendar_id:
        calendar = Calendar.query.filter(Calendar.id == calendar_id).first()
        return render_template("newcalendar.html", user=user, calendar=calendar)

    calendars = Calendar.query.all()
    return render_template("calendars.html", user=user, calendars=calendars)


@app.route('/newcalendar', methods=['GET', 'POST'])
def newcalendar():
    # Conditions *************************************
    if DEBUG:
        pdb.set_trace()
    user = User.query.filter(User.ext_id_hashed==session.get('profile_ext_id_hashed')).first()
    if (user is None):
        session.clear()
        return redirect(url_for('index'))
    elif (user.account_status == 0):
        return render_template("message.html",
                               message="Please wait for admin approval. Contact an admin if needed.",
                               avatar_url=user.avatar_url)
    elif (user.account_type != 2):
        return render_template("message.html", message="You do not have proper right to access this site. Please contact an admin if needed.", avatar_url=user.avatar_url)
    # End of conditions ******************************
    calendar_action = ""
    calendar_action = request.values.get('calendar_action', '')
    if calendar_action:
        new_name = request.values.get('new_name', '')
        calendar_id = request.values.get('calendar_id', '')
        if calendar_action == "add":
            try:
                calendar = Calendar(name=new_name)
                db.session.add(calendar)
                db.session.commit()
            except Exception:
                db.session.rollback()
        if calendar_action == "rename":
            try:
                calendar = Calendar.query.filter(Calendar.id == calendar_id).first()
                calendar.name = new_name
                db.session.commit()
            except Exception:
                db.session.rollback()
        if calendar_action == "delete":
            if calendar_id != 1 :
                try:
                    calendar = Calendar.query.filter(Calendar.id == calendar_id).first()
                    vacation_data = Holiday.query.filter(Holiday.calendar_id == calendar_id).all()

                    for vacation in vacation_data:
                        db.session.delete(vacation)
                    db.session.delete(calendar)
                    db.session.commit()
                except Exception:
                    db.session.rollback()
        #elif calendar_action == "cancel":
        return redirect("/calendars")
    return render_template("newcalendar.html", user=user, calendar=None)


@app.route('/logout')
def logout():
    try:
        session.clear()
    except Exception:
        pass
    return redirect("home")


@app.route('/reset')
def reset():
    database = createDB(hostname=ConfigData.DB_HOSTNAME)
    createTables()
    setupDB()
    return redirect(url_for('index'))


if __name__ == "__main__":
    context=('./app/self.vacation.crt','./app/self.vacation.key')
    app.run(host="0.0.0.0", port=5000, debug=DEBUG_FLASK, ssl_context=context)