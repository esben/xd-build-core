from xd.build.core.target import *
from xd.build.core.manifest import *
from xd.build.core.buildq import *
import os

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

parser_help = 'Build recipe'

def add_arguments(parser):
    parser.add_argument(
        'target', nargs='+',
        help='build target (recipe or task to build)')
    return

def run(args, manifest, env):
    manifest = Manifest(manifest)
    targets = [Target(target) for target in args.target]
    for target in targets:
        if not target.task:
            target.task = 'all'
            # TODO: implement default tasks in metadata, so that each recipe
            # knows if fx. package or deploy (or both, or some other task) is
            # the target task if no specific task is specified (or if all is
            # specified).
        if not target.type:
            target.type = 'machine'
    cookbook = manifest.cookbook()
    tasks = [cookbook.get_task(target) for target in targets]
    buildq = BuildQueue(manifest)
    for task in tasks:
        buildq.add_task(task)

    # Go through all tasks (in dependency order), calculating the desired task
    # signature (ie. metadata + dependency signature)
    buildq.close()

    # TODO: go through all tasks (in dependency order), running them
    return buildq.run_all()
