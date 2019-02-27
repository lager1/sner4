"""scheduler commands"""

import click
from netaddr import IPNetwork
from flask.cli import with_appcontext
from sner.server.controller.scheduler.task import task_targets_action
from sner.server.extensions import db
from sner.server.model.scheduler import Profile, Task


@click.group(name='scheduler', help='sner.server scheduler management')
def scheduler_command():
	"""scheduler commands click group/container"""
	pass


@scheduler_command.command(name='task_list', help='task listing')
@with_appcontext
def task_list():
	"""list tasks"""

	headers = ['id', 'name', 'profile', 'targets', 'created', 'modified']
	fmt = '%-4s %-20s %-40s %-8s %-30s %-30s'
	print(fmt % tuple(headers))
	for task in Task.query.all():
		print(fmt % (task.id, task.name, task.profile, len(task.targets), task.created, task.modified))


@scheduler_command.command(name='task_add', help='add a new task')
@click.argument('profile_id', type=int)
@click.argument('targets', nargs=-1)
@click.option('--name')
@click.option('--group_size', type=int, default=5)
@click.option('--priority', type=int, default=10)
@click.option('--file', type=click.File('r'))
@with_appcontext
def task_add(profile_id, targets, **kwargs):
	"""add new task"""

	profile = Profile.query.filter(Profile.id == profile_id).one_or_none()
	if not profile:
		raise RuntimeError('no such profile')

	targets = list(targets)
	if kwargs["file"]:
		targets += kwargs["file"].read().splitlines()
	task = Task(name=kwargs["name"], profile=profile, targets=targets, group_size=kwargs["group_size"], priority=kwargs["priority"])
	db.session.add(task)
	db.session.commit()


@scheduler_command.command(name='task_delete', help='delete task')
@click.argument('task_id', type=int)
@with_appcontext
def task_delete(task_id):
	"""delete task"""

	task = Task.query.filter(Task.id == task_id).one_or_none()
	if not task:
		raise RuntimeError('no such task')
	db.session.delete(task)
	db.session.commit()


@scheduler_command.command(name='task_targets', help='task targets action')
@click.argument('task_id', type=int)
@click.argument('action')
@with_appcontext
def task_targets(task_id, action):
	"""schedule/unschedule targets of the task"""

	task = Task.query.filter(Task.id == task_id).one_or_none()
	if not task:
		raise RuntimeError('no such task')
	task_targets_action(task, action)


@scheduler_command.command(name='enumips', help='enumerate ip address range')
@click.argument('targets', nargs=-1)
@click.option('--file', type=click.File('r'))
def enumips(targets, **kwargs):
	"""enumerate ip address range"""

	targets = list(targets)
	if kwargs["file"]:
		targets += kwargs["file"].read().splitlines()
	for item in targets:
		for tmp in IPNetwork(item).iter_hosts():
			print(tmp)
