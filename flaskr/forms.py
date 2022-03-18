from flask_wtf import FlaskForm
from wtforms import PasswordField, validators, EmailField, HiddenField

class StravaCredsForm(FlaskForm):
    email = EmailField('email', [validators.DataRequired()])
    password = PasswordField('password', [validators.DataRequired()])
    athlete_id = HiddenField(validators=[validators.DataRequired()])