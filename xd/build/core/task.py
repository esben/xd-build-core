import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


import xd.build.core.data.task
from .data.namespace import flattened
import os
import stat
import shlex
from sh import docker


__all__ = ['Task', 'InvalidTaskName']


class InvalidTaskName(Exception):
    pass


class Task(object):
    """XD-build task."""

    def __init__(self, recipe, name):
        """Task constructor.

        Arguments:
        recipe -- Recipe instance
        name -- name of task, fx. 'compile'
        """
        try:
            self.task = recipe.data[name]
        except KeyError:
            raise InvalidTaskName(name)
        if not isinstance(self.task, xd.build.core.data.task.Task):
            raise InvalidTaskName(name)
        self.recipe = recipe
        self.name = name

    def prepare(self, tmpdir):
        self.files = {}
        data = self.recipe.data.copy()
        assert not 'TASK' in data
        data['TASK'] = self.name
        # FIXME: run task_hooks

        tasks = set([var for var in data.values()
                 if isinstance(var, xd.build.core.data.task.Task)
                     and var.name != self.name])

        self.prepare_env_sh(data)
        self.prepare_data_py(data)
        self.prepare_run_sh()
        for filename, filedata in self.files.items():
            path = os.path.join(tmpdir, filename)
            with open(path, 'w') as file:
                file.write(filedata)
            if path[-3:] in ('.py', '.sh'):
                os.chmod(path, stat.S_IRWXU|stat.S_IRWXG
                         |stat.S_IROTH|stat.S_IXOTH)

    def prepare_env_sh(self, data):
        def env_sh_filter(var):
            if var.name.startswith('_'):
                return False
            if not getattr(var, 'env', False):
                return False
            return True
        env_data = flattened(data, filter=env_sh_filter)
        self.files['env.sh'] = ""
        for name, value in sorted(env_data.items()):
            self.files['env.sh'] += "export %s=%s\n"%(
                name, shlex.quote(str(value)))

    def prepare_data_py(self, data):
        func = self.task.get()
        if func is None:
            return
        self.files['data.py'] = """#!/usr/bin/env python3

{0}
_pre_functions = []
_main_function = {1}
_post_functions = []

if __name__ == '__main__':
    for pre_function in _pre_functions:
        pre_function()
    _main_function()
    for post_function in _post_functions:
        post_function()
""".format(data.dump(filter=self.dump_filter),
           data[self.name].get().__name__)

    def prepare_run_sh(self):
        self.files['run.sh'] = """#!/usr/bin/env bash
source /xd/task/env.sh
/xd/task/data.py
"""
            
    def dump_filter(self, name, value):
        if name.startswith('_'):
            return False
        if isinstance(value, xd.build.core.data.task.Task):
            return False
        return True

    def __str__(self):
        return '%s:%s'%(self.recipe, self.name)

    def run(self, manifest):
        if not self.recipe.data[self.name].get():
            print('Skipping noop %s'%(self))
            return
        print('Running %s'%(self))
        if self.recipe.version is None:
            recipe_name = self.recipe.name
        else:
            recipe_name = '%s_%s'%(self.recipe.name, self.recipe.version)
        tmpdir = os.path.join(manifest.tmpdir,
                              recipe_name, self.recipe.type, self.name)
        if not os.path.exists(tmpdir):
            os.makedirs(tmpdir)
        self.prepare(tmpdir)
        args = ['--volume={}:/xd/task'.format(tmpdir)]
        for host_dir, container_dir, ro in self.task._mount:
            host_dir = self.task.eval(host_dir)
            container_dir = self.task.eval(container_dir)
            arg = '--volume={}:{}'.format(host_dir, container_dir)
            if ro:
                arg += ':ro'
            if not os.path.exists(host_dir):
                os.makedirs(host_dir)    
            args.append(arg)
        if self.recipe.version is not None:
            recipe_version = self.recipe.version
        else:
            recipe_version = ''
        self.container = '_'.join(
            ['xd-build', self.recipe.type, self.recipe.name, recipe_version,
             self.name])
        print('Container', self.container)
        args.append('--name={}'.format(self.container))
        parent_image = 'xd-build'
        parent_task = self.task.parent()
        if parent_task:
            parent_image = '_'.join([parent_image,
                                     self.recipe.type, self.recipe.name,
                                     recipe_version, parent_task])
            parent_image += ':SHA1SIGNATURE'
        print('Parent image', parent_image)
        args += [parent_image, '/xd/task/run.sh']
        #if docker.inspect(self.container).exit_code == 0:
        #    docker.rm(self.container)
        result = docker.run(*args)
        print(result.strip())
        print('exit_code', result.exit_code)
        if result.exit_code == 0:
            self.image = '{}:SHA1SIGNATURE'.format(self.container)
            docker.commit([self.container, self.image])
            docker.tag([self.image, self.container])
            docker.rm(self.container)
