from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, Email, DataRequired, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])


class Registration(FlaskForm):
    f_name = StringField('First Name:', validators=[InputRequired()])
    l_name = StringField('Last Name', validators=[InputRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email(
        message=('Please enter a valid email address.'))])
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', [
        DataRequired(message="Please enter a password."),
    ])


class AddFriend(FlaskForm):
    username = StringField('Enter the username for the user you wish to add', validators=[InputRequired()])
    type = SelectField('Choose their Category', choices=[(0, 'Select an option'), (
        'Relative', 'Relative'), ('School', 'School'), ('Work', 'Work')])


class newGroup(FlaskForm):
    grp_name = StringField('Group Name:', validators=[InputRequired()])
    purpose = StringField('Purpose:', validators=[InputRequired()])
    CEusername = StringField(
        'Add Content Editor by Username:', validators=[InputRequired()])


class joinGrp(FlaskForm):
    grp_name = StringField('Enter the name of the group you wish to join', validators=[InputRequired()])


class createPost(FlaskForm):
    photo = FileField(validators=[FileRequired()])
    grp_name = StringField('Group Name:', validators=[InputRequired()])


class NewPost(FlaskForm):
    description = TextAreaField(validators=[InputRequired()])
    photo = FileField(validators=[FileAllowed(['jpg', 'png', 'Images only!'])])


class Search(FlaskForm):
    searchTerm = StringField('searchTerm', validators=[InputRequired()])


class ProPicUpload(FlaskForm):
    profPic = FileField(
        validators=[FileRequired(), FileAllowed(['jpg', 'png', 'Images only!'])])


class CEForm(FlaskForm):
    CEusername = StringField('username', validators=[InputRequired()])
