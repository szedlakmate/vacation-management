# *************************************************
#                 CONFIGURATION DATA
# *************************************************

# This file holds data for the Vacation Management application

class ConfigData():
    # Debugging options
    DEBUG_FLASK = True # Start the webserver in debug mode
    DEBUG = False # Reach pdb.set_trace() breakpoints. In order to use, the container MUST be started the following way:
                  # docker-compose run --service-ports web

    # Database configuration
    DB_HOSTNAME = 'mysqlserver'
    DB_DATABASE = 'vacation'
    DB_PASSWORD = 'password'
    DB_USER = 'root'

    # Google authentication data
    # You must configure these 3 values from Google APIs console
    # https://code.google.com/apis/console          mateszedlak@invenshure.com
    GOOGLE_LOGIN_CLIENT_SECRET = 'qAH_V-G5Gx49uk1VmsoVioo4'
    GOOGLE_LOGIN_CLIENT_ID = '945161050960-9uafb16faeljklnvpu8gp31h5u23l517.apps.googleusercontent.com'
    GOOGLE_LOGIN_REDIRECT_SCHEME = 'https'
    GOOGLE_SECRET_KEY = 'secret'

    # Initial database data
    BASE_USERS = [] #[{'id':1, 'username':'root', 'nickname':'root', 'google_id':'0', 'avatar':None, 'email': 'foo:bar', 'birthday':'1900-01-01', 'account_status':1}]
    BASE_CALENDARS = [{'id':1, 'name':'Normal holiday', 'free_days':20},{'id':2, 'name':'Sick-leave', 'free_days':-1}]
    BASE_GROUPS = [{'id':1, 'name':'Office'}]

    # Email settings
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT=465
    MAIL_USE_SSL=True
    MAIL_USE_TLS=False
    MAIL_USERNAME='demo.szedlak@gmail.com'
    MAIL_PASSWORD='SbaUEknYxMmngW4J2ZCG'
    MAIL_DEFAULT_SENDER='demo.szedlak@gmail.com'

    # Calendar configuration
    CAL_COLORMAP = ['green', 'cornflowerblue', 'yellow', 'red', 'amber', 'purple',
                'pink']  # Must be in sync with the default.css file