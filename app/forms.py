from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired, Email, DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])


class Registration(FlaskForm):
    f_name = StringField('First Name:', validators=[InputRequired()])
    l_name = StringField('Last Name', validators=[InputRequired()])
    email = StringField('Email Address', validators=[ DataRequired(), Email(message=('Please enter a valid email address.'))])
    l_name = StringField('Last Name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', [
        DataRequired(message="Please enter a password."),
    ])
    confirmPassword = PasswordField('Repeat Password', [
        EqualTo('password', message='Passwords must match.')
    ])

class AddFriend(FlaskForm):
    username = StringField('Friend Username', validators=[InputRequired()])
    type = SelectField('What is your personality type?', choices=[(0, 'Select an option'), (
        'Relative', 'Relative'), ('School', 'School'), ('Work', 'Work')])

class newGroup(FlaskForm):
    grp_name = StringField('Group Name:', validators=[InputRequired()])
    purpose = StringField('Purpose:', validators=[InputRequired()])
