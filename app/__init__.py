from flask import Flask
UPLOAD_FOLDER = 'C:\\Users\\Loretta\\Desktop\\MyBook\\app\\static\\uploads'
# UPLOAD_FOLDER = 'C:\\Program Files\\heroku\\flasky\\DB-2020\\app\\static\\uploads'

SECRET_KEY = 'secretK3y'

app = Flask(__name__)

app.config.from_object(__name__)
from app import views
