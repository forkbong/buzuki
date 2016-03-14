from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField
from wtforms.validators import DataRequired


class SongForm(FlaskForm):
    name = StringField('Name', [DataRequired()])
    artist = StringField('Artist', [DataRequired()])
    body = TextAreaField('Body', [DataRequired()])
    link = StringField('YouTube link')


class PasswordForm(FlaskForm):
    password = PasswordField('Password', [DataRequired()])
