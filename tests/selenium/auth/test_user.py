# This file is part of sner4 project governed by MIT license, see the LICENSE.txt file.
"""
selenium ui tests for auth.user component
"""

from flask import url_for
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from sner.server import db
from sner.server.model.auth import User
from tests.selenium import dt_inrow_delete, dt_rendered, WEBDRIVER_WAIT


def test_user_list_route(live_server, sl_admin, test_user):  # pylint: disable=unused-argument
    """simple test ajaxed datatable rendering"""

    sl_admin.get(url_for('auth.user_list_route', _external=True))
    dt_rendered(sl_admin, 'user_list_table', test_user.username)


def test_user_list_route_inrow_delete(live_server, sl_admin, test_user):  # pylint: disable=unused-argument
    """delete user inrow button"""

    sl_admin.get(url_for('auth.user_list_route', _external=True))
    # in this test-case there are multiple items in the table (current_user, test_user), hence index which to delete has to be used
    dt_inrow_delete(sl_admin, 'user_list_table', 1)
    assert not User.query.filter(User.id == test_user.id).one_or_none()


def test_user_apikey_route(live_server, sl_admin, test_user):  # pylint: disable=unused-argument
    """apikey generation/revoking feature tests"""

    sl_admin.get(url_for('auth.user_list_route', _external=True))
    dt_rendered(sl_admin, 'user_list_table', test_user.username)

    # disable fade, the timing interferes with the test
    sl_admin.execute_script('$("div#modal-global").toggleClass("fade")')

    sl_admin.find_element_by_xpath('//a[@data-url="%s"]' % url_for('auth.user_apikey_route', user_id=test_user.id, action='generate')).click()
    WebDriverWait(sl_admin, WEBDRIVER_WAIT).until(
        EC.visibility_of_element_located((By.XPATH, '//h4[@class="modal-title" and text()="Apikey operation"]')))
    sl_admin.find_element_by_xpath('//div[@id="modal-global"]//button[@class="close"]').click()
    WebDriverWait(sl_admin, WEBDRIVER_WAIT).until(EC.invisibility_of_element_located((By.XPATH, '//div[@class="modal-global"')))
    dt_rendered(sl_admin, 'user_list_table', test_user.username)
    user = User.query.filter(User.id == test_user.id).one_or_none()
    assert user.apikey
    db.session.expunge(user)

    sl_admin.find_element_by_xpath('//a[@data-url="%s"]' % url_for('auth.user_apikey_route', user_id=test_user.id, action='revoke')).click()
    WebDriverWait(sl_admin, WEBDRIVER_WAIT).until(
        EC.visibility_of_element_located((By.XPATH, '//h4[@class="modal-title" and text()="Apikey operation"]')))
    sl_admin.find_element_by_xpath('//div[@id="modal-global"]//button[@class="close"]').click()
    WebDriverWait(sl_admin, WEBDRIVER_WAIT).until(EC.invisibility_of_element_located((By.XPATH, '//div[@class="modal-global"')))
    dt_rendered(sl_admin, 'user_list_table', test_user.username)
    user = User.query.filter(User.id == test_user.id).one_or_none()
    assert not user.apikey
