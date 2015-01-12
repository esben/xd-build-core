import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


from .var import *
from .expr import *
from .func import *
import types
import sys


__all__ = ['Task']


class Task(Variable):

    __slots__ = ['_before', '_after', '_mount', '_merge', '_capture']

    basetype = types.FunctionType
    empty = ''

    def __init__(self, value=None, scope=None, before=None, after=None):
        super(Task, self).__init__(value, scope)
        self._before = set()
        self._after = set()
        if before:
            self.before(before)
        if after:
            self.after(after)
        self._mount = []
        self._merge = []
        self._capture = []

    def prepare_value(self, value):
        value = super(Task, self).prepare_value(value)
        if isinstance(value, self.basetype):
            raise TypeError('invalid type for %s variable <%s>: %s'%(
                self.__class__.__name__, getattr(self, 'name', ''),
                value.__class__.__name__))
        if value and self.scope:
            function = self.scope.eval(value, wrapper=False)
            if not isinstance(function, Function):
                raise TypeError('invalid type for %s variable <%s>: %s'%(
                    self.__class__.__name__, getattr(self, 'name', ''),
                    value.__class__.__name__))
            if function and hasattr(function, 'name'):
                self.scope[function.name].filter(Expression(
                    "TASK=='{}' or TASK is None".format(self.name)))
        return value

    def before(self, value):
        if isinstance(value, (list, set)):
            for task in value:
                self.before(task)
        else:
            self._before.add(value)

    def after(self, value):
        if isinstance(value, (list, set)):
            for task in value:
                self.after(task)
        else:
            self._after.add(value)

    def parent(self):
        parents = self.parents()
        if not parents:
            return None
        if len(parents) > 1:
            raise Exception('multiple parents')
        return parents.pop()
            
    def parents(self, pure=True):
        tasks = [var for var in self.scope.values()
                 if isinstance(var, Task) and var != self]
        names = [task.name for task in tasks]
        # First, remove all non-existing tasks from after list
        after = self._after.intersection(names)
        # Then add all tasks that wants to come before
        for task in tasks:
            if self.name in task._before:
                after.add(task.name)
        # Finally, remove all non-direct ancestors, so that only parents that
        # are not grand parents or ...
        if pure:
            for task in after:
                after = after.difference(self.scope[task].ancestors())
        return after

    def ancestors(self):
        # First get all parents
        after = self.parents(pure=False)
        # then add all their ancestors
        for task in after:
            after = after.union(self.scope[task].ancestors())
            # TODO: maybe implement explicit detection of circular task
            # dependencies
        return after

    def dump(self, stream=None):
        value = self.get()
        if value:
            value = "Expression('{}')".format(value.__name__)
        else:
            value = 'None'
        print('{}=Task({}, before={}, after={})'.format(
            self.name, value, self._before or None, self._after or None),
              file=stream or sys.stdout)

    def mount(self, host, container, ro=False):
        '''Bind mount a host directory to a container directory.

        Arguments:
        host -- host directory path, absolute or relative
        container -- container directory path
        ro -- True: read-only mount, False: read-write mount
        '''
        self._mount.append((host, container, ro))

    def merge(self, container, host):
        '''Merge content of container directory with host directory.

        When the task is completed, the content of container directory is
        merged into the host directory.  In case of merge conflicts, the host
        content is overwritten.

        Arguments:
        container -- container directory path
        host -- host directory path, absolute or relative
        '''
        self._merge.append((container, host))

    def capture(self, container):
        '''Capture container directory as task output.

        Arguments:
        container -- container directory path
        '''
        self._capture.append(container)
