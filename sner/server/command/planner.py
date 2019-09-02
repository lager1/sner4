# This file is part of sner4 project governed by MIT license, see the LICENSE.txt file.
"""
sner planner module
"""


@click.group(name='planner', help='sner.server planner management')
def planner_command():
    """planner commands click group/container"""


@planner_command.command(name='run', help='run planner daemon')
@with_appcontext
def storage_import():

    target_networks = [1, 2, 3]

    # SETUP

    # ensure service discovery task
    # ensure service discovery queue
    # ensure service version scan task
    # ensure service version scan queue

    # EXECUTION

    # enqueue all enumerated targets
    # monitor queue/job
        # for every completed job in SD queue
            # parse services from output, enqueue to SV queue
            # delete completed job

        # for every completed job in SV queue
            # import output to storage
            # delete completed job

    # cleanup storage
