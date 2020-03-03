# This file is part of sner4 project governed by MIT license, see the LICENSE.txt file.
"""
db commands
"""

import os
import shutil

import click
from flask import current_app
from flask.cli import with_appcontext

from sner.server import db
from sner.server.model.auth import User
from sner.server.model.scheduler import Excl, ExclFamily, Queue, Task, Target
from sner.server.model.storage import Host, Note, Service, SeverityEnum, Vuln


def db_remove():
    """remove database artefacts (including var content)"""

    db.session.close()
    db.drop_all()

    path = current_app.config['SNER_VAR']
    for file_object in os.listdir(path):
        file_object_path = os.path.join(path, file_object)
        if os.path.isdir(file_object_path):
            shutil.rmtree(file_object_path)
        else:
            os.unlink(file_object_path)


@click.group(name='db', help='sner.server db management')
def db_command():
    """db command group/container"""


@db_command.command(name='init', help='initialize database schema')
@with_appcontext
def db_init():  # pragma: no cover
    """initialize database schema"""

    db.create_all()


@db_command.command(name='init-data', help='put initial data to database')
@with_appcontext
def db_initdata():  # pylint: disable=too-many-statements
    """put initial data to database"""

    # auth test data
    db.session.add(User(username='user1', active=True, roles=['user', 'operator', 'admin']))

    # scheduler test data
    db.session.add(Excl(family=ExclFamily.network, value='127.66.66.0/26', comment='blacklist 1'))
    db.session.add(Excl(family=ExclFamily.regex, value=r'.*donotscan.*', comment='blacklist 2'))

    task = Task(
        name='dev_010 dummy',
        module='dummy',
        params='--dummyparam 1',
        group_size=3)
    db.session.add(task)
    queue = Queue(task=task, name=task.name, priority=10, active=True)
    db.session.add(queue)
    for target in range(100):
        db.session.add(Target(target=target, queue=queue))

    task = Task(
        name='pentest_010 dns recon',
        module='nmap',
        params='-sL    -Pn --reason',
        group_size=20)
    db.session.add(task)
    queue = Queue(task=task, name=task.name, priority=10)
    db.session.add(queue)
    for target in range(100):
        db.session.add(Target(target='10.0.0.%d' % target, queue=queue))

    task = Task(
        name='pentest_020 full tcp scan',
        module='nmap',
        params='-sS -A -p1-65535    -Pn --reason --min-hostgroup 20 --min-rate 900 --max-rate 1500 --max-retries 3',
        group_size=20)
    db.session.add(task)
    db.session.add(Queue(task=task, name=task.name, priority=10))

    task = Task(
        name='meta_010 userspace tcp',
        module='nmap',
        params='-sT -A    -Pn --reason --min-hostgroup 20 --min-rate 100 --max-rate 200',
        group_size=20)
    db.session.add(task)
    db.session.add(Queue(task=task, name=task.name, priority=10))

    task = Task(
        name='sner_010 top1000 ack scan',
        module='nmap',
        params='-sA --top-ports 1000    -Pn --reason --min-hostgroup 400 --min-rate 4000 --max-rate 4500',
        group_size=400)
    db.session.add(task)
    db.session.add(Queue(task=task, name=task.name, priority=10))

    task = Task(
        name='sner_011 top10000 ack scan',
        module='nmap',
        params='-sA --top-ports 10000    -Pn --reason --min-hostgroup 1000 --min-rate 8000 --max-rate 8500',
        group_size=1000)
    db.session.add(task)
    db.session.add(Queue(task=task, name=task.name, priority=10))

    # for sweeps max-rate and max-hostgroup are not really necessary because of how manymap works,
    # but we'll left it there for manual testing inspiration
    task = Task(
        name='sner_020 inet version scan basic',
        module='manymap',
        params='-sV --version-intensity 4    -Pn --reason --scan-delay 10 --max-rate 1 --max-hostgroup 1',
        group_size=50)
    db.session.add(task)
    db.session.add(Queue(task=task, name=task.name + ' commonports', priority=20))
    db.session.add(Queue(task=task, name=task.name + ' normal', priority=10))

    task = Task(
        name='sner_025 inet version scan intense',
        module='manymap',
        params='-sV --version-intensity 8    -Pn --reason --scan-delay 10 --max-rate 1 --max-hostgroup 1',
        group_size=50)
    db.session.add(task)
    db.session.add(Queue(task=task, name=task.name, priority=10))

    task = Task(
        name='sner_030 ftp sweep',
        module='manymap',
        params='-sC --script ftp-anon.nse    -Pn --reason --scan-delay 10 --max-rate 1 --max-hostgroup 1',
        group_size=50)
    db.session.add(task)
    db.session.add(Queue(task=task, name=task.name, priority=10))

    task = Task(
        name='sner_031 http titles',
        module='manymap',
        params='-sC --script http-title.nse    -Pn --reason --scan-delay 10 --max-rate 1 --max-hostgroup 1',
        group_size=50)
    db.session.add(task)
    db.session.add(Queue(task=task, name=task.name, priority=10))

    task = Task(
        name='sner_032 ldap rootdse',
        module='manymap',
        params='-sC --script ldap-rootdse.nse    -Pn --reason --scan-delay 10 --max-rate 1 --max-hostgroup 1',
        group_size=50)
    db.session.add(task)
    db.session.add(Queue(task=task, name=task.name, priority=10))

    # storage test data
    host = Host(
        address='127.4.4.4',
        hostname='testhost.testdomain.test<script>alert(1);</script>',
        os='Test Linux 1',
        comment='a some unknown service server')
    db.session.add(host)

    db.session.add(Service(
        host=host,
        proto='tcp',
        port=12345,
        state='open:testreason',
        name='testservice',
        info='testservice banner',
        comment='manual testservice comment'))

    db.session.add(Vuln(
        host=host,
        name='test vulnerability',
        xtype='testxtype.123',
        severity=SeverityEnum.critical,
        comment='a test vulnerability comment',
        refs=['ref1', 'ref2'],
        tags=['tag1', 'tag2']))

    db.session.add(Vuln(
        host=host,
        name='another test vulnerability',
        xtype='testxtype.124',
        severity=SeverityEnum.high,
        comment='another vulnerability comment',
        tags=None))

    db.session.add(Vuln(
        host=host,
        name='vulnerability1',
        xtype='testxtype.124',
        severity=SeverityEnum.medium,
        tags=['info']))

    db.session.add(Vuln(
        host=host,
        name='vulnerability2',
        xtype='testxtype.124',
        severity=SeverityEnum.low,
        tags=['report']))

    db.session.add(Vuln(
        host=host,
        name='vulnerability2',
        xtype='testxtype.124',
        severity=SeverityEnum.info,
        tags=['info']))

    db.session.add(Vuln(
        host=host,
        name='vulnerability3',
        xtype='testxtype.124',
        severity=SeverityEnum.unknown,
        tags=['report']))

    db.session.add(Note(
        host=host,
        xtype='sner.testnote',
        data='testnote data',
        comment='test note comment'))

    db.session.commit()


@db_command.command(name='remove', help='remove database (including var content)')
@with_appcontext
def db_remove_command():
    """db remove command stub"""

    db_remove()
