"""auth forms"""

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, validators


class LoginForm(FlaskForm):
    """login form"""

    username = StringField(label='Username', validators=[validators.InputRequired()])
    password = PasswordField(label='Password', validators=[validators.InputRequired()])
