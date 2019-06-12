"""auth forms"""

from flask import current_app
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectMultipleField, StringField, ValidationError, validators, widgets

from sner.server.password_supervisor import PasswordSupervisor


def strong_password(form, field):
    """validate password field"""

    if field.data:
        pwsr = PasswordSupervisor().check_strength(field.data, form.username.data)
        if not pwsr.is_strong:
            raise ValidationError(pwsr.message)


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class LoginForm(FlaskForm):
    """login form"""

    username = StringField(label='Username', validators=[validators.InputRequired()])
    password = PasswordField(label='Password', validators=[validators.InputRequired()])


class UserForm(FlaskForm):
    """user edit form"""

    username = StringField(label='Username', validators=[validators.Length(min=1, max=256)])
    password = PasswordField(label='Password', validators=[strong_password])
    email = StringField(label='Email', validators=[validators.Length(max=256)])
    active = BooleanField(label='Active')
    roles = MultiCheckboxField(label='Roles')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.roles.choices = [(x, x) for x in current_app.config['SNER_AUTH_ROLES']]
