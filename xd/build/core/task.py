import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


import xd.build.core.data.task
from .data.namespace import flattened
import os
import stat
import shlex
import sh
from sh import docker
import hashlib


__all__ = ['Task', 'InvalidTaskName']


class InvalidTaskName(Exception):
    pass


def first_item(var):
    return var[0]


class TaskSignature(object):

    def __init__(self):
        self.m = hashlib.md5()

    def __str__(self):
        return self.m.hexdigest()

    def digest(self):
        return self.m.digest()

    def update(self, msg):
        if isinstance(msg, TaskSignature):
            msg = str(msg)
        if isinstance(msg, str):
            msg = msg.encode('utf-8')
        self.m.update(msg)
        self.m.update(b'\0')


class Task(object):
    """XD-build task."""

    def __init__(self, recipe, name):
        """Task constructor.

        Arguments:
        recipe -- Recipe instance
        name -- name of task, fx. 'compile'
        """
        try:
            self.data = recipe.data[name]
        except KeyError:
            raise InvalidTaskName(name)
        if not isinstance(self.data, xd.build.core.data.task.Task):
            raise InvalidTaskName(name)
        self.recipe = recipe
        self.name = name

    def __str__(self):
        return '%s:%s'%(self.recipe, self.name)

    def parent(self):
        parent = self.data.parent()
        if not parent:
            return None
        return self.recipe.get_task(parent)

    def prepare(self):
        self.files = {}
        data = self.recipe.data.copy()
        assert not 'TASK' in data
        data['TASK'] = self.name
        # FIXME: run task_prepare_hooks
        # Git rid of other tasks
        for other_task in [var for var in data.values()
                           if isinstance(var, xd.build.core.data.task.Task)
                           and var.name != self.name]:
            del data[other_task.name]
        self.prepare_run_sh()
        self.prepare_env_sh(data)
        self.prepare_data_py(data)
        self.signature = TaskSignature()
        for filename, content in sorted(self.files.items(), key=first_item):
            self.signature.update(filename)
            self.signature.update(content)

    def prepare_run_sh(self):
        self.files['run.sh'] = """#!/usr/bin/env bash
source /xd/task/env.sh
/xd/task/data.py
"""

    def prepare_env_sh(self, data):
        def env_sh_filter(var):
            if var.name.startswith('_'):
                return False
            if not getattr(var, 'env', False):
                return False
            return True
        env_data = flattened(data, filter=env_sh_filter)
        self.files['env.sh'] = ""
        for name, value in sorted(env_data.items(), key=first_item):
            self.files['env.sh'] += "export %s=%s\n"%(
                name, shlex.quote(str(value)))

    def prepare_data_py(self, data):
        func = data[self.name].get()
        if func:
            main_function = func.__name__
        else:
            main_function = None
        self.files['data.py'] = """#!/usr/bin/env python3

{0}
_pre_functions = []
_main_function = {1}
_post_functions = []

if __name__ == '__main__':
    for pre_function in _pre_functions:
        pre_function()
    if _main_function:
        _main_function()
    for post_function in _post_functions:
        post_function()
""".format(data.dump(filter=self.dump_filter), main_function)
            
    def dump_filter(self, name, value):
        if name.startswith('_'):
            return False
        if isinstance(value, xd.build.core.data.task.Task):
            return False
        return True

    def write(self, tmpdir):
        if not os.path.exists(tmpdir):
            os.makedirs(tmpdir)
        for filename, filedata in self.files.items():
            path = os.path.join(tmpdir, filename)
            with open(path, 'w') as file:
                file.write(filedata)
            if path[-3:] in ('.py', '.sh'):
                os.chmod(path, stat.S_IRWXU|stat.S_IRWXG
                         |stat.S_IROTH|stat.S_IXOTH)

    def recipe_version(self):
        if self.recipe.version is not None:
            return self.recipe.version
        else:
            return ''

    def container(self):
        return '_'.join(
            ['xd-build', self.recipe.type, self.recipe.name,
             self.recipe_version(), self.name])

    def image(self):
        return '{}:{}'.format(self.container(), self.signature)

    def isdone(self):
        try:
            docker.inspect(self.image())
        except sh.ErrorReturnCode:
            return False
        return True
   
    def run(self, base_tmpdir):
        if self.recipe.version is None:
            recipe_name = self.recipe.name
        else:
            recipe_name = '%s_%s'%(self.recipe.name, self.recipe.version)
        tmpdir = os.path.join(base_tmpdir,
                              recipe_name, self.recipe.type, self.name)
        #if not self.recipe.data[self.name].get():
        #    print('Skipping noop %s'%(self))
        #    return
        print('Running %s'%(self))
        self.write(tmpdir)
        args = ['--volume={}:/xd/task'.format(tmpdir)]
        for host_dir, container_dir, ro in self.data._mount:
            host_dir = self.data.eval(host_dir)
            container_dir = self.data.eval(container_dir)
            arg = '--volume={}:{}'.format(host_dir, container_dir)
            if ro:
                arg += ':ro'
            if not os.path.exists(host_dir):
                os.makedirs(host_dir)    
            args.append(arg)
        container = self.container()
        print('Container', self.container())
        args.append('--name={}'.format(container))
        parent_image = 'xd-build'
        parent_task = self.parent()
        if parent_task:
            parent_image = '_'.join([parent_image,
                                     self.recipe.type, self.recipe.name,
                                     self.recipe_version(), parent_task.name])
            parent_image += ':{}'.format(parent_task.signature)
        print('Parent image', parent_image)
        args += [parent_image, '/xd/task/run.sh']
        #if docker.inspect(self.container).exit_code == 0:
        #    docker.rm(self.container)
        result = docker.run(*args)
        result_str = result.strip()
        if result:
            print(result)
        print('exit_code', result.exit_code)
        if result.exit_code == 0:
            image = self.image()
            docker.commit([container, image])
            docker.tag([image, container])
            docker.rm(container)
