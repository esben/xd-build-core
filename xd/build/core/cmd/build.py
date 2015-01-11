from xd.build.core.target import *
from xd.build.core.manifest import *
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
        if not target.type:
            target.type = 'machine'
    cookbook = manifest.cookbook()
    targets = [cookbook.get_task(target) for target in targets]
    # FIXME: these targets (=tasks) should be added to buildqueue which should
    # add all needed task dependencies
    for task in targets:
        task.run(manifest)
    return
