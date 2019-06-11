"""auth controler tests"""

from http import HTTPStatus
from uuid import uuid4

from flask import url_for

from sner.server import db
from sner.server.model.auth import User


def test_login(client, test_user):
    """test login"""

    tmp = User.query.filter(User.id == test_user.id).one_or_none()
    tmp_password = str(uuid4())
    tmp.password = tmp_password
    db.session.commit()

    form = client.get(url_for('auth.login_route')).form
    form['username'] = test_user.username
    form['password'] = tmp_password
    response = form.submit()
    assert response.status_code == HTTPStatus.FOUND

    response = client.get(url_for('auth.login_test_route'))
    assert 'Logged in as: %s' % test_user.username in response.body.decode('utf-8')
