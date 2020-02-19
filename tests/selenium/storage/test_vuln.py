# This file is part of sner4 project governed by MIT license, see the LICENSE.txt file.
"""
selenium ui tests for storage.vuln component
"""

from flask import url_for
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from sner.server import db
from sner.server.model.storage import Vuln
from tests.selenium import dt_inrow_delete, dt_rendered, dt_wait_processing, WEBDRIVER_WAIT
from tests.selenium.storage import check_select_rows, check_vulns_multiactions


def check_vulns_filtering(selenium, dt_id):
    """test vuln views filtering functions"""

    toolbar_id = '%s_toolbar' % dt_id

    # there should be 4 rows in total
    dt_elem = dt_wait_processing(selenium, dt_id)
    assert len(dt_elem.find_elements_by_xpath('//tbody/tr[@role="row"]')) == 4

    # one not tagged
    selenium.find_element_by_id(toolbar_id).find_element_by_xpath('//a[text()="Not tagged"]').click()
    dt_elem = dt_wait_processing(selenium, dt_id)
    assert len(dt_elem.find_elements_by_xpath('//tbody/tr[@role="row"]')) == 1
    assert dt_elem.find_element_by_xpath('//td/a[text()="vuln 1"]')

    # three tagged
    selenium.find_element_by_id(toolbar_id).find_element_by_xpath('//a[text()="Tagged"]').click()
    dt_elem = dt_wait_processing(selenium, dt_id)
    assert len(dt_elem.find_elements_by_xpath('//tbody/tr[@role="row"]')) == 3
    assert not dt_elem.find_elements_by_xpath('//td/a[text()="vuln 1"]')

    # two already reviewed
    selenium.find_element_by_id(toolbar_id).find_element_by_xpath('//a[text()="Exclude reviewed"]').click()
    dt_elem = dt_wait_processing(selenium, dt_id)
    assert len(dt_elem.find_elements_by_xpath('//tbody/tr[@role="row"]')) == 2
    assert dt_elem.find_element_by_xpath('//td/a[text()="vuln 1"]')
    assert dt_elem.find_element_by_xpath('//td/a[text()="vuln 2"]')

    # one should go directly to report
    selenium.find_element_by_id(toolbar_id).find_element_by_xpath('//a[text()="Only Report"]').click()
    dt_elem = dt_wait_processing(selenium, dt_id)
    assert len(dt_elem.find_elements_by_xpath('//tbody/tr[@role="row"]')) == 1
    assert dt_elem.find_element_by_xpath('//td/a[text()="vuln 4"]')

    # and user must be able to loose the filter
    selenium.find_element_by_xpath('//a[text()="unfilter"]').click()
    dt_elem = dt_wait_processing(selenium, dt_id)
    assert len(dt_elem.find_elements_by_xpath('//tbody/tr[@role="row"]')) == 4


def test_vuln_list_route(live_server, sl_operator, test_vuln):  # pylint: disable=unused-argument
    """simple test ajaxed datatable rendering"""

    sl_operator.get(url_for('storage.vuln_list_route', _external=True))
    dt_rendered(sl_operator, 'vuln_list_table', test_vuln.comment)


def test_vuln_list_route_inrow_delete(live_server, sl_operator, test_vuln):  # pylint: disable=unused-argument
    """delete vuln inrow button"""

    sl_operator.get(url_for('storage.vuln_list_route', _external=True))
    dt_inrow_delete(sl_operator, 'vuln_list_table')
    assert not Vuln.query.filter(Vuln.id == test_vuln.id).one_or_none()


def test_vuln_list_route_selectrows(live_server, sl_operator, test_vulns_multiaction):  # pylint: disable=unused-argument
    """test dt selection and selection buttons"""

    sl_operator.get(url_for('storage.vuln_list_route', _external=True))
    check_select_rows(sl_operator, 'vuln_list_table')


def test_vuln_list_route_multiactions(live_server, sl_operator, test_vulns_multiaction):  # pylint: disable=unused-argument
    """test vulns multiactions"""

    sl_operator.get(url_for('storage.vuln_list_route', _external=True))
    check_vulns_multiactions(sl_operator, 'vuln_list_table')


def test_vuln_list_route_filtering(live_server, sl_operator, test_vulns_filtering):  # pylint: disable=unused-argument
    """test list vulns view filtering features"""

    sl_operator.get(url_for('storage.vuln_list_route', _external=True))
    check_vulns_filtering(sl_operator, 'vuln_list_table')


def test_vuln_view_route_tagging(live_server, sl_operator, test_vuln):  # pylint: disable=unused-argument
    """test vuln view tagging features"""

    sl_operator.get(url_for('storage.vuln_view_route', vuln_id=test_vuln.id, _external=True))

    sl_operator.find_element_by_xpath('//a[contains(@class, "abutton_vuln_tag_set") and text()="Info"]').click()
    WebDriverWait(sl_operator, WEBDRIVER_WAIT).until(
        EC.visibility_of_element_located((By.XPATH, '//span[contains(@class, "tag-label") and contains(text(), "info")]')))
    vuln = Vuln.query.get(test_vuln.id)
    assert 'info' in vuln.tags

    sl_operator.find_element_by_xpath('//span[contains(@class, "tag-label") and contains(text(), "info")]/a[@class="abutton_vuln_tag_unset"]').click()
    assert not sl_operator.find_elements_by_xpath('//span[contains(@class, "tag-label") and contains(text(), "info")]')
    db.session.refresh(vuln)
    assert 'info' not in vuln.tags


def test_vuln_grouped_route(live_server, sl_operator, test_vuln):  # pylint: disable=unused-argument
    """test grouped vulns view"""

    sl_operator.get(url_for('storage.vuln_grouped_route', _external=True))
    dt_wait_processing(sl_operator, 'vuln_grouped_table')
    assert len(sl_operator.find_elements_by_xpath('//tbody/tr[@role="row"]')) == 1


def test_vuln_grouped_route_filtering(live_server, sl_operator, test_vulns_filtering):  # pylint: disable=unused-argument
    """test grouped vulns view filtering features"""

    sl_operator.get(url_for('storage.vuln_grouped_route', _external=True))
    check_vulns_filtering(sl_operator, 'vuln_grouped_table')
