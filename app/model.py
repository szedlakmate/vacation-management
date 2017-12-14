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


class User(db.Model):
    # Data Model User Table
    id = db.Column(db.Integer, primary_key=True)
    id_hash = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, username, nickname, google_id, avatar, email, birthday, id=None, account_status=None):
        # initialize columns
        if id:
            self.id = id

    def __repr__(self):
        return '<User %r>' % self.username
    # Hashes shall be refreshed after certain time (eg. at every bootup)


class CalendarType(db.Model):
    # Data Model User Table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name, id=None):
        # initialize columns
        if id:
            self.id = id
        self.name = name


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
            newcalendar = CalendarType(name=calendar['name'], id=calendar['id'])
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