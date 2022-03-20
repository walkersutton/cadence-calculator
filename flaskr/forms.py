from flask_wtf import FlaskForm
from wtforms import PasswordField, validators, EmailField, HiddenField


class StravaCredsForm(FlaskForm):
    email = EmailField('Strava Email', [validators.DataRequired()])
    password = PasswordField('Strava Password', [validators.DataRequired()])
    athlete_id = HiddenField(validators=[validators.DataRequired()])
