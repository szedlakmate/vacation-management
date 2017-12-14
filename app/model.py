from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import datetime


# Database Configurations
from sqlalchemy import ForeignKey

app = Flask(__name__)
DATABASE = 'vacation'
PASSWORD = 'password'  # XXX Need to be read from config file
USER = 'root'
HOSTNAME = 'mysqlserver'

BASEUSERS = [] #[{'id':1, 'username':'root', 'nickname':'root', 'google_id':'0', 'avatar':None, 'email': 'foo:bar', 'birthday':'1900-01-01', 'account_status':1}]
BASECALENDARS = [{'id':1, 'name':'Normal holiday'},{'id':2, 'name':'Sick-leave'}]
# XXX Need to be read from config file


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s'%(USER, PASSWORD, HOSTNAME, DATABASE)
db = SQLAlchemy(app)

# Database migration command line
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


def hashid(hashable):
    return hash(str(hashable) & "mfkFJ_5_SIDOfsd" & str(hashable))


class User(db.Model):
    # User model
    id = db.Column(db.Integer, primary_key=True)
    ext_id = db.Column(db.String(200), unique=True, nullable=False) # XXX prefix should be added
    ext_id_hashed = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), unique=False, nullable=False)
    nickname = db.Column(db.String(8), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    avatar_url = db.Column(db.String(200), unique=False, default="https://t3.ftcdn.net/jpg/00/64/67/52/240_F_64675209_7ve2XQANuzuHjMZXP3aIYIpsDKEbF5dD.jpg")
    birthday = db.Column(db.Date, unique=False, nullable=False)     # XXX Should be Nullable
    account_type = db.Column(db.Integer, unique=False, nullable=False, default=0)
    account_status = db.Column(db.Integer, unique=False, nullable=False, default=0)
    account_created = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.datetime.utcnow)

    def __init__(self, ext_id, name, nickname, email, birthday, avatar_url=None, id=None, account_type= None, account_status=None):
        if id:
            self.id = id
        self.ext_id = ext_id
        self.ext_id_hashed = hashid(ext_id)
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

    # XXX Hashes shall be refreshed after certain time (eg. at every bootup)


class Calendar(db.Model):
    # Calendar types model
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name, id=None):
        # initialize columns
        if id:
            self.id = id
        self.name = name


class Holiday(db.Model):
    # Holiday event model
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("user.id"), nullable=False)
    calendar_id = db.Column(db.Integer, ForeignKey("calendar.id"), nullable=False)
    start = db.Column(db.Date, unique=False, nullable=False)
    end = db.Column(db.Date, unique=False, nullable=False)
    note = db.Column(db.String(15), unique=False, nullable=True)
    status = db.Column(db.Integer, unique=False, nullable=False, default = 0)

    def __init__(self, user_id, calendar_id, start, end, id=None, note=None):
        # initialize columns
        if id:
            self.id = id
        self.user_id = user_id
        self.calendar_id = calendar_id
        self.start = start
        self.end = end
        if note:
            self.note = note


class Group(db.Model):
    # Group types model
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name, id=None):
        # initialize columns
        if id:
            self.id = id
        self.name = name


class Group_members(db.Model):
    # Calendar types model
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, ForeignKey("group.id"), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey("user.id"), nullable=False)

    def __init__(self, group_id, user_id, id=None):
        # initialize columns
        if id:
            self.id = id
        self.group_id = group_id
        self.user_id = user_id


class createDB():
    def __init__(self, hostname=None):
        import sqlalchemy
        if hostname is not None:
            HOSTNAME = hostname
        engine = sqlalchemy.create_engine('mysql://%s:%s@%s'%(USER, PASSWORD, HOSTNAME)) # connect to server
        resetDB(engine)
        engine.execute("CREATE DATABASE IF NOT EXISTS %s "%(DATABASE))


def resetDB(engine):
    try:
        engine.execute("DROP DATABASE %s "%(DATABASE))
    except:
        db.session.rollback()


def setupDB():
    from sqlalchemy.exc import IntegrityError
    import simplejson as json
    for user in BASEUSERS:
        try:
            profile = User(username=user['username'], nickname=user['nickname'], google_id=user['google_id'],
                               avatar=user['avatar'], email=user['email'], birthday=user['birthday'], account_status=user['account_status'], id=user['id'])
            db.session.add(profile)
            db.session.commit()
        #except KeyError:  # IntegrityError:
        #    db.session.rollback()
        except IntegrityError:
            db.session.rollback()
            return json.dumps(
                    {'Integrity error was raised:': 'Please check the given data or contact the administrator'})
    for calendar in BASECALENDARS:
        try:
            newcalendar = Calendar(name=calendar['name'], id=calendar['id'])
            db.session.add(newcalendar)
            db.session.commit()
        except KeyError:  # IntegrityError:
            db.session.rollback()
        except IntegrityError:
            db.session.rollback()
            return json.dumps(
                    {'Integrity error was raised:': 'Please check the given data or contact the administrator'})


def createTables():
    from sqlalchemy.exc import IntegrityError
    try:
        db.create_all()
    except IntegrityError:
        db.session.rollback()


if __name__ == '__main__':
    manager.run()