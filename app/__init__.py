from flask import Flask
from flask_login import LoginManager

UPLOAD_FOLDER = './static/uploads'
SECRET_KEY = 'secretK3y'

app = Flask(__name__)

# Flask-Login login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config.from_object(__name__)
from app import views
