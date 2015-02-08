from xd.build.core.manifest import *
from xd.build.core.docker import *
import os


import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


parser_help = 'Manage XD-build docker-in-docker container'


def add_arguments(parser):
    parser.add_argument('--name', dest='container_name', default='xd-build',
                        help='name of XD-build docker-in-docker container')
    subparsers = parser.add_subparsers(title='XD-build docker commands',
                                       dest='subcommand')
    subparser = subparsers.add_parser(
        'start',
        help='Start XD-build docker-in-docker container')
    subparser = subparsers.add_parser(
        'stop',
        help='Stop XD-build docker-in-docker container')
    subparser = subparsers.add_parser(
        'sh',
        help='Get a shell prompt in XD-build docker-in-docker container')
    return

def run(args, manifest, env):
    log.debug(args)
    if not '/' in args.container_name:
        args.container_name = '/' + args.container_name
    client = DockerClient()
    if args.subcommand == 'start':
        client.start()
    elif args.subcommand == 'stop':
        client.stop()
    elif args.subcommand == 'sh':
        client_container = client.start()
        return os.system('docker exec -ti %s /bin/bash'%(client_container))
    return
