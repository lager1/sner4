"""auth component models"""

import flask_login

from sner.server import db


class User(db.Model, flask_login.UserMixin):
    """user model"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True)
    password = db.Column(db.String(256))
    email = db.Column(db.String(256))
    active = db.Column(db.Boolean)

    @property
    def is_active(self):
        return self.active

# TODO: there's is_authenticated return True in mixin, why ?
