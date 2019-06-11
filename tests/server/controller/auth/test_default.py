"""auth controler tests"""

from http import HTTPStatus

from flask import url_for


def test_login(client, test_user):
    """test login"""

    form = client.get(url_for('auth.login_route')).form
    form['username'] = test_user.username
    form['password'] = test_user.password
    response = form.submit()
    assert response.status_code == HTTPStatus.FOUND

    response = client.get(url_for('auth.login_test_route'))
    assert 'Logged in as: %s' % test_user.username in response.body.decode('utf-8')
