from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import datetime
from sqlalchemy import ForeignKey
from config import ConfigData           # Configuration


# *************************************************
#                     DATA MODEL
# *************************************************

# This data model file holds all the database descriptions.

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s' \
                                        %(ConfigData.DB_USER,
                                          ConfigData.DB_PASSWORD,
                                          ConfigData.DB_HOSTNAME,
                                          ConfigData.DB_DATABASE)
db = SQLAlchemy(app)

# Database migration command line
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


def hash_id(hashable):
    return hash(str(hashable) + "mfkF")


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ext_id = db.Column(db.String(200), unique=True, nullable=False)         # Prefix should be added like 'google_'
    ext_id_hashed = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), unique=False, nullable=False)
    nickname = db.Column(db.String(10), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    avatar_url = db.Column(db.String(200), unique=False,
                           default="https://t3.ftcdn.net/jpg/00/64/67/52/"
                                   "240_F_64675209_7ve2XQANuzuHjMZXP3aIYIpsDKEbF5dD.jpg")
    birthday = db.Column(db.Date, unique=False, nullable=False)     # Nullable should be enabled to manually set later.
    account_type = db.Column(db.Integer, unique=False, nullable=False, default=0)
    account_status = db.Column(db.Integer, unique=False, nullable=False, default=0)
    account_created = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.datetime.utcnow)

    def __init__(self, ext_id, name, nickname, email, birthday, avatar_url=None, id=None,
                 account_type=None, account_status=None):
        if id:
            self.id = id
        self.ext_id = ext_id
        self.ext_id_hashed = hash_id(ext_id)
        self.name = name
        self.nickname = nickname
        self.email = email
        self.birthday = birthday
        if avatar_url:
            self.avatar_url = avatar_url
        if account_type:
            self.account_type = account_type
        if account_status:
            self.account_status = account_status

    def __repr__(self):
        return '<User %r>' % self.nickname


# Calendar types model
class Calendar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    free_days = db.Column(db.Integer, default=-1, nullable=False, unique=False)

    def __init__(self, name, id=None, free_days=None):
        # initialize columns
        if id:
            self.id = id
        if free_days:
            self.free_days = free_days
        self.name = name

    def __repr__(self):
        return self.name


# Holiday data
class Holiday(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(200), ForeignKey("user.ext_id"), nullable=False)
    calendar_id = db.Column(db.Integer, ForeignKey("calendar.id"), nullable=False)
    start = db.Column(db.Date, unique=False, nullable=False)
    end = db.Column(db.Date, unique=False, nullable=False)
    url = db.Column(db.String(200), nullable=True)
    note = db.Column(db.String(15), unique=False, nullable=True)
    status = db.Column(db.Integer, unique=False, nullable=False, default=0)

    def __init__(self, user_id, calendar_id, start, end, id=None, note=None, url=None):
        # initialize columns
        if id:
            self.id = id
        self.user_id = user_id
        self.calendar_id = calendar_id
        self.start = start
        self.end = end
        if url:
            self.url = url
        if note:
            self.note = note


# Group types model
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name, id=None):
        # initialize columns
        if id:
            self.id = id
        self.name = name


# Group member data
class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, ForeignKey("group.id"), nullable=False)
    user_id = db.Column(db.String(200), ForeignKey("user.ext_id"), nullable=False)

    def __init__(self, group_id, user_id, id=None):
        # initialize columns
        if id:
            self.id = id
        self.group_id = group_id
        self.user_id = user_id


# Connecting to the mysql service and creating database if needed
class CreateDB:
    def __init__(self):
        import sqlalchemy
        engine = sqlalchemy.create_engine('mysql://%s:%s@%s' %(ConfigData.DB_USER,
                                                               ConfigData.DB_PASSWORD,
                                                               ConfigData.DB_HOSTNAME))     # connect to server
        reset_db(engine)
        engine.execute("CREATE DATABASE IF NOT EXISTS %s " % ConfigData.DB_DATABASE)


# Reset: deleting previous traces
def reset_db(engine):
    try:
        engine.execute("DROP DATABASE %s " % ConfigData.DB_DATABASE)
    except Exception:
        db.session.rollback()


# Creating tables
def create_tables():
    from sqlalchemy.exc import IntegrityError
    try:
        db.create_all()
    except IntegrityError:
        db.session.rollback()


# Setting up the initial records
def setup_db():
    from sqlalchemy.exc import IntegrityError
    import simplejson as json
    for user in ConfigData.BASE_USERS:
        try:
            profile = User(name=user['name'],
                           nickname=user['nickname'],
                           ext_id=user['ext_id'],
                           avatar_url=user['avatar_url'],
                           email=user['email'],
                           birthday=user['birthday'],
                           account_type=user['account_type'],
                           account_status=user['account_status'],
                           id=user['id'])

            db.session.add(profile)
            db.session.commit()
        except KeyError:
            db.session.rollback()
        except IntegrityError:
            db.session.rollback()
            return json.dumps(
                    {'Integrity error was raised:': 'Please check the given data or contact the administrator'})

    for calendar in ConfigData.BASE_CALENDARS:
        try:
            new_calendar = Calendar(name=calendar['name'], id=calendar['id'], free_days=calendar['free_days'])
            db.session.add(new_calendar)
            db.session.commit()
        except KeyError:
            db.session.rollback()
        except IntegrityError:
            db.session.rollback()
            return json.dumps(
                    {'Integrity error was raised:': 'Please check the given data or contact the administrator'})

    for group in ConfigData.BASE_GROUPS:
        try:
            new_group = Group(name=group['name'], id=group['id'])
            db.session.add(new_group)
            db.session.commit()
        except KeyError:
            db.session.rollback()
        except IntegrityError:
            db.session.rollback()
            return json.dumps(
                {'Integrity error was raised:': 'Please check the given data or contact the administrator'})


if __name__ == '__main__':
    manager.run()
