from flask import current_app as app
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms import HiddenField, PasswordField, StringField, TextAreaField
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
    password = PasswordField('Κωδικός', [DataRequired('Έλα σε παρακαλώ πολύ')])
    next = HiddenField('next')

    def validate(self, *args, **kwargs):
        if not super().validate(*args, **kwargs):
            return False

        password = self.password.data
        pwhash = app.config['PWHASH']
        if not check_password_hash(pwhash, password):
            self.password.errors.append('Λάθος κωδικός')
            return False

        return True
