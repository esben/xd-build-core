import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


import sh
import re
import docker
from requests.exceptions import HTTPError


__all__ = ['DockerClient']


class DockerClient(object):
    """XD-build Docker Client."""

    def __init__(self, dind_container='xd-build', dind_image='xdembedded/dind',
                 host_url='unix://var/run/docker.sock'):
        """Docker Client constructor."""
        version = sh.docker.version()
        # TODO: add error handling for failure in 'docker version' command
        server_version = re.search(r'^Server API version: ([\d\.]+)$',
                                   version.stdout.decode('utf-8'),
                                   flags=re.MULTILINE)
        # TODO: add error handling for match failure
        server_version = server_version.group(1)
        self.host_client = docker.Client(base_url=host_url,
                                         version=server_version)
        if not dind_container.startswith('/'):
            dind_container = '/' + dind_container
        self.dind_container = dind_container
        self.dind_image = dind_image

    def host_container(self, name):
        for container in self.host_client.containers(all=True):
            if name in container['Names']:
                return container
        return None

    def host_container_state(self, container):
        inspect = self.host_client.inspect_container(container['Id'])
        # TODO: add error handling on inspect failing
        return inspect['State']

    def start(self):
        container = self.host_container(self.dind_container)
        if not container:
            container = self.host_client.create_container(
                image=self.dind_image, name=self.dind_container,
                hostname='xd-build', detach=True,
                environment=['PORT=2375'], ports=[2375])
        if not self.host_container_state(container)['Running']:
            self.host_client.start(
                container['Id'], privileged=True, port_bindings={2375: None})
        return container['Id']

    def stop(self):
        container = self.host_container(self.dind_container)
        if not container:
            return
        response = self.host_client.stop(container['Id'], timeout=5)
