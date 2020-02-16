# This file is part of sner4 project governed by MIT license, see the LICENSE.txt file.
"""
flask forms
"""

import re
from ipaddress import ip_network

from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SelectField, StringField, SubmitField, TextAreaField, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Length, NumberRange

from sner.server.form import TextAreaListField
from sner.server.model.scheduler import ExclFamily, Task


def valid_excl_family(form, field):  # pylint: disable=unused-argument
    """validate exclusion family"""

    if field.data not in ExclFamily.__members__.values():
        raise ValidationError('Invalid family')


def valid_excl_value(form, field):
    """validate exclusion value"""

    if form.family.data == ExclFamily.network:
        try:
            ip_network(field.data)
        except ValueError as e:
            raise ValidationError(str(e))
    elif form.family.data == ExclFamily.regex:
        try:
            re.compile(field.data)
        except re.error:
            raise ValidationError('Invalid regex')


def tasks():
    """returns list of tasks for selectfiled"""
    return Task.query.all()


class TaskForm(FlaskForm):
    """profile edit form"""

    name = StringField('Name', [InputRequired(), Length(min=1, max=250)])
    module = StringField('Module', [InputRequired(), Length(min=1, max=250)])
    params = TextAreaField('Parameters', render_kw={'rows': '10'})
    submit = SubmitField('Save')


class QueueForm(FlaskForm):
    """queue edit form"""

    name = StringField('Name', [InputRequired(), Length(min=1, max=250)])
    task = QuerySelectField('Task', [InputRequired()], query_factory=tasks, allow_blank=False, get_label='name')
    group_size = IntegerField('Group size', [InputRequired(), NumberRange(min=1)], default=1)
    priority = IntegerField('Priority', [InputRequired()], default=0)
    active = BooleanField('Active')
    submit = SubmitField('Save')


class QueueEnqueueForm(FlaskForm):
    """queue enqueue form"""

    targets = TextAreaListField('Targets', [InputRequired()], render_kw={'rows': '10'})
    submit = SubmitField('Enqueue')


class ExclForm(FlaskForm):
    """exclustion edit form"""

    family = SelectField('Family', [InputRequired(), valid_excl_family], choices=ExclFamily.choices(), coerce=ExclFamily.coerce)
    value = StringField('Value', [InputRequired(), Length(min=1), valid_excl_value])
    comment = TextAreaField('Comment')
    submit = SubmitField('Save')


class ExclImportForm(FlaskForm):
    """exclusions list import form"""

    data = TextAreaField('Data', [InputRequired()], render_kw={'rows': '10'})
    replace = BooleanField('Replace')
    submit = SubmitField('Import')
