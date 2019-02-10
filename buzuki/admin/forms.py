from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField
from wtforms.validators import URL, DataRequired


class SongForm(FlaskForm):
    name = StringField('Name', [DataRequired()])
    artist = StringField('Artist', [DataRequired()])
    scale = TextAreaField('Scale', [DataRequired()])
    rhythm = TextAreaField('Rhythm', [DataRequired()])
    body = TextAreaField('Body', [DataRequired()])
    link = StringField('YouTube link', [DataRequired(), URL()])


class PasswordForm(FlaskForm):
    password = PasswordField('Password', [DataRequired()])
