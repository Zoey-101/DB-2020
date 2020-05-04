from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)

app.secret_key = 'some_secret'

# Flask-Login login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config.from_object(__name__)
from app import views
