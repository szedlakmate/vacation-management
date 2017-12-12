from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import datetime


# Database Configurations
from sqlalchemy import ForeignKey

app = Flask(__name__)
DATABASE = 'vacation'
PASSWORD = 'password'
USER = 'root'
HOSTNAME = 'mysqlserver'


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


class CreateDB():
    def __init__(self, hostname=None):
        if hostname is not None:
            HOSTNAME = hostname
        import sqlalchemy
        engine = sqlalchemy.create_engine('mysql://%s:%s@%s'%(USER, PASSWORD, HOSTNAME)) # connect to server
        ResetDB(engine)
        engine.execute("CREATE DATABASE IF NOT EXISTS %s "%(DATABASE)) #create db


def ResetDB(engine):
    try:
        engine.execute("DROP DATABASE %s "%(DATABASE))
    except:
        pass


if __name__ == '__main__':
    manager.run()