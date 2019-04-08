from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField
from wtforms.validators import URL, DataRequired


class SongForm(FlaskForm):
    name = StringField('Τίτλος', [DataRequired('Ο τίτλος είναι υποχρεωτικός')])
    artist = StringField(
        'Καλλιτέχνης', [DataRequired('Ο καλλιτέχνης είναι υποχρεωτικός')]
    )
    scale = TextAreaField(
        'Δρόμος', [DataRequired('Ο δρόμος είναι υποχρεωτικός')]
    )
    rhythm = TextAreaField(
        'Ρυθμός', [DataRequired('Ο ρυθμός είναι υποχρεωτικός')]
    )
    body = TextAreaField(
        'Τραγούδι', [DataRequired('Το τραγούδι είναι υποχρεωτικό')]
    )
    link = StringField(
        'YouTube link', [
            DataRequired('Το link είναι υποχρεωτικό'),
            URL(message='Αυτό δεν ήταν URL')
        ]
    )


class PasswordForm(FlaskForm):
    password = PasswordField('Password', [DataRequired()])
