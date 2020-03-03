# This file is part of sner4 project governed by MIT license, see the LICENSE.txt file.
"""
sqlalchemy models
"""
# pylint: disable=too-few-public-methods,abstract-method

import os
import re
from datetime import datetime
from ipaddress import ip_network

from flask import current_app
from sqlalchemy.orm import relationship, validates

from sner.server import db
from sner.server.model import SelectableEnum


class Task(db.Model):
    """holds settings/arguments for type of scan/scanner. eg. host discovery, fast portmap, version scan, ..."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    module = db.Column(db.String(250), nullable=False)
    params = db.Column(db.Text)
    group_size = db.Column(db.Integer, nullable=False)

    queues = relationship('Queue', back_populates='task', cascade='delete,delete-orphan', passive_deletes=True)

    def __repr__(self):
        return '<Task %d: %s>' % (self.id, self.name)


class Queue(db.Model):
    """task assignment for specific targets"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id', ondelete='CASCADE'), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=False)

    task = relationship('Task', back_populates='queues')
    targets = relationship('Target', back_populates='queue', cascade='delete,delete-orphan', passive_deletes=True)
    jobs = relationship('Job', back_populates='queue', cascade='delete,delete-orphan', passive_deletes=True)

    def __repr__(self):
        return '<Queue %d: %s>' % (self.id, self.name)

    @property
    def data_abspath(self):
        """return absolute path of the queue data directory"""
        return os.path.join(current_app.config['SNER_VAR'], 'scheduler', 'queue-%s' % self.id) if self.id else None


class Target(db.Model):
    """single target of the task"""

    id = db.Column(db.Integer, primary_key=True)
    target = db.Column(db.Text, nullable=False)
    queue_id = db.Column(db.Integer, db.ForeignKey('queue.id', ondelete='CASCADE'), nullable=False)

    queue = relationship('Queue', back_populates='targets')

    def __repr__(self):
        return '<Target %d: %s>' % (self.id, self.target)


class Job(db.Model):
    """assigned job"""

    id = db.Column(db.String(36), primary_key=True)
    queue_id = db.Column(db.Integer, db.ForeignKey('queue.id', ondelete='CASCADE'))
    assignment = db.Column(db.Text, nullable=False)
    retval = db.Column(db.Integer)
    time_start = db.Column(db.DateTime, default=datetime.utcnow)
    time_end = db.Column(db.DateTime)

    queue = relationship('Queue', back_populates='jobs')

    def __repr__(self):
        return '<Job %s>' % self.id

    @property
    def output_abspath(self):
        """return absolute path to the output data file acording to current app config"""
        return os.path.join(self.queue.data_abspath, self.id)


class ExclFamily(SelectableEnum):
    """exclusion family enum"""

    network = 'network'
    regex = 'regex'


class Excl(db.Model):
    """exclusion model, used for target blacklisting by network ranges or
    regex; typicaly values for the model would be enforced by apropriate forms,
    but since exclusions allows to import from user data, model should ensure
    corect values itself
    """

    id = db.Column(db.Integer, primary_key=True)
    family = db.Column(db.Enum(ExclFamily), nullable=False)
    value = db.Column(db.Text, nullable=False)
    comment = db.Column(db.Text)

    def __repr__(self):
        return '<Excl %s>' % self.id

    @validates('family')
    def validate_family(self, key, new_family):  # pylint: disable=unused-argument
        """validate family and subsequently value for the family"""

        if new_family not in ExclFamily.__members__.values():
            raise ValueError('Invalid family')

        if self.value:
            if new_family == ExclFamily.network:
                ip_network(self.value)
            if new_family == ExclFamily.regex:
                try:
                    re.compile(self.value)
                except re.error:
                    raise ValueError('Invalid regex')

        return new_family

    @validates('value')
    def validate_value(self, key, new_value):  # pylint: disable=unused-argument
        """validate value acording to the current family"""

        if self.family == ExclFamily.network:
            ip_network(new_value)
        if self.family == ExclFamily.regex:
            try:
                re.compile(new_value)
            except re.error:
                raise ValueError('Invalid regex')

        return new_value
