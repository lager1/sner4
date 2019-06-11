"""auth component models"""

import flask_login
from sqlalchemy.dialects import postgresql

from sner.server import db


class User(db.Model, flask_login.UserMixin):
    """user model"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True)
    password = db.Column(db.String(256))
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
