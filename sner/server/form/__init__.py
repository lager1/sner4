# This file is part of sner4 project governed by MIT license, see the LICENSE.txt file.
"""
flask forms
"""

from flask_wtf import FlaskForm
from wtforms import TextAreaField


class LinesField(TextAreaField):
    """textarea transparently handling list of items"""

    # value to form
    def _value(self):
        if self.data:
            return '\n'.join(self.data)
        return ''

    # value from form
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0].splitlines()  # pylint: disable=attribute-defined-outside-init
        else:
            self.data = []  # pylint: disable=attribute-defined-outside-init


class ButtonForm(FlaskForm):
    """generic button form"""
