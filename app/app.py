from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'


if __name__ == "__main__":
    ssl_context=('./app/self.vacation.crt','./app/self.vacation.key')
    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=ssl_context)
    #app.add_url_rule('/favicon.ico',
    #                 redirect_to=url_for('static', filename='img/favicon.ico'))