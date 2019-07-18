# This file is part of sner4 project governed by MIT license, see the LICENSE.txt file.
"""
controller queue tests
"""

import json
from http import HTTPStatus

from flask import url_for

from sner.server.model.scheduler import Queue
from tests.server.model.scheduler import create_test_queue, create_test_target


def test_queue_list_route(cl_operator, test_target):
    """queue list route test"""

    response = cl_operator.get(url_for('scheduler.queue_list_route'))
    assert response.status_code == HTTPStatus.OK
    assert '<h1>Queues list' in response


def test_queue_list_json_route(cl_operator, test_queue):
    """queue list_json route test"""

    response = cl_operator.post(url_for('scheduler.queue_list_json_route'), {'draw': 1, 'start': 0, 'length': 1, 'search[value]': test_queue.name})
    assert response.status_code == HTTPStatus.OK
    response_data = json.loads(response.body.decode('utf-8'))
    assert response_data['data'][0]['name'] == test_queue.name

    response = cl_operator.post(
        url_for('scheduler.queue_list_json_route', filter='Queue.name=="%s"' % test_queue.name),
        {'draw': 1, 'start': 0, 'length': 1})
    assert response.status_code == HTTPStatus.OK
    response_data = json.loads(response.body.decode('utf-8'))
    assert response_data['data'][0]['name'] == test_queue.name


def test_queue_add_route(cl_operator, test_task):
    """queue add route test"""

    test_queue = create_test_queue(test_task)

    form = cl_operator.get(url_for('scheduler.queue_add_route')).form
    form['name'] = test_queue.name
    form['task'] = test_queue.task.id
    form['group_size'] = test_queue.group_size
    form['priority'] = test_queue.priority
    response = form.submit()
    assert response.status_code == HTTPStatus.FOUND

    queue = Queue.query.filter(Queue.name == test_queue.name).one_or_none()
    assert queue
    assert queue.name == test_queue.name


def test_queue_edit_route(cl_operator, test_queue):
    """queue edit route test"""

    form = cl_operator.get(url_for('scheduler.queue_edit_route', queue_id=test_queue.id)).form
    form['name'] = form['name'].value+' edited'
    response = form.submit()
    assert response.status_code == HTTPStatus.FOUND

    queue = Queue.query.filter(Queue.id == test_queue.id).one_or_none()
    assert queue.name == form['name'].value


def test_queue_enqueue_route(cl_operator, test_queue):
    """queue enqueue route test"""

    test_target = create_test_target(test_queue)

    form = cl_operator.get(url_for('scheduler.queue_enqueue_route', queue_id=test_queue.id)).form
    form['targets'] = test_target.target
    response = form.submit()
    assert response.status_code == HTTPStatus.FOUND

    queue = Queue.query.filter(Queue.id == test_queue.id).one_or_none()
    assert queue.targets[0].target == test_target.target


def test_queue_flush_route(cl_operator, test_target):
    """queue flush route test"""

    test_queue_id = test_target.queue_id

    form = cl_operator.get(url_for('scheduler.queue_flush_route', queue_id=test_queue_id)).form
    response = form.submit()
    assert response.status_code == HTTPStatus.FOUND

    queue = Queue.query.filter(Queue.id == test_queue_id).one_or_none()
    assert not queue.targets


def test_queue_delete_route(cl_operator, test_queue):
    """queue delete route test"""

    form = cl_operator.get(url_for('scheduler.queue_delete_route', queue_id=test_queue.id)).form
    response = form.submit()
    assert response.status_code == HTTPStatus.FOUND

    queue = Queue.query.filter(Queue.id == test_queue.id).one_or_none()
    assert not queue
