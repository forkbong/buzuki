from flask import current_app as app
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms import HiddenField, PasswordField, StringField, TextAreaField
from wtforms.validators import URL, DataRequired, Optional, ValidationError


class Year:
    def __call__(self, form, field):
        data = field.data
        if not data:
            return
        try:
            year = int(data)
        except ValueError:
            raise ValidationError('Αυτή δεν ήταν σοβαρή χρονολογία')
        if year < 1800 or year > 2100:
            raise ValidationError('Αυτή δεν ήταν σοβαρή χρονολογία')


class SongForm(FlaskForm):
    name = StringField('Τίτλος', [DataRequired('Ο τίτλος είναι υποχρεωτικός')])
    year = StringField('Έτος', [Year()])
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
            Optional(),
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
