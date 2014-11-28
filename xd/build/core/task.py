import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


import xd.build.core.data.task
from .data.namespace import flattened
import os
import stat
import shlex

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
            task = recipe.data[name]
        except KeyError:
            raise InvalidTaskName(name)
        if not isinstance(task, xd.build.core.data.task.Task):
            raise InvalidTaskName(name)
        self.recipe = recipe
        self.name = name

    def prepare(self, tmpdir):
        self.files = {}
        data = self.recipe.data.copy()
        assert not 'TASK' in data
        data['TASK'] = self.name
        # FIXME: run task_hooks
        self.prepare_task_py(data)
        self.prepare_task_sh(data)
        for filename, filedata in self.files.items():
            path = os.path.join(tmpdir, filename)
            with open(path, 'w') as file:
                file.write(filedata)
            if path[-3:] in ('.py', '.sh'):
                os.chmod(path, stat.S_IRWXU|stat.S_IRWXG
                         |stat.S_IROTH|stat.S_IXOTH)

    def prepare_task_py(self, data):
        self.files['task.py'] = """#!/usr/bin/env python3

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

    def prepare_task_sh(self, data):
        def task_sh_filter(var):
            if var.name.startswith('_'):
                return False
            if not getattr(var, 'env', False):
                return False
            return True
        env_data = flattened(data, filter=task_sh_filter)
        self.files['env.sh'] = ""
        for name, value in sorted(env_data.items()):
            self.files['env.sh'] += "export %s=%s\n"%(
                name, shlex.quote(str(value)))

    def dump_filter(self, name, value):
        if name.startswith('_'):
            return False
        if isinstance(value, xd.build.core.data.task.Task):
            return False
        return True

    def __str__(self):
        return '%s:%s'%(self.recipe, self.name)

    def run(self, tmpdir):
        print('Running %s'%(self))
        if self.recipe.version is None:
            recipe_name = self.recipe.name
        else:
            recipe_name = '%s_%s'%(self.recipe.name, self.recipe.version)
        tmpdir = os.path.join(tmpdir, recipe_name, self.recipe.type, self.name)
        if not os.path.exists(tmpdir):
            os.makedirs(tmpdir)
        self.prepare(tmpdir)
