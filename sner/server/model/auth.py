"""auth component models"""

from crypt import crypt, mksalt, METHOD_SHA512

import flask_login
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property

from sner.server import db


class User(db.Model, flask_login.UserMixin):
    """user model"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True)
    _password = db.Column('password', db.String(256))
    email = db.Column(db.String(256))
    active = db.Column(db.Boolean)
    roles = db.Column(postgresql.ARRAY(db.String, dimensions=1))

    @property
    def is_active(self):
        return self.active

    def has_role(self, role):
        """shortcut function to check user has role"""

        if self.roles and (role in self.roles):
            return True
        return False

    @hybrid_property
    def password(self):
        return self._password;

    @password.setter
    def password(self, value):
        self._password = crypt(value, mksalt(METHOD_SHA512))

    def force_password(self, value):
        self._password = value

    @property
    def password_salt(self):
        if self._password:
            return self._password[:self.password.rfind('$')]
        return None
