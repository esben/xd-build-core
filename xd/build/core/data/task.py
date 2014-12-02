import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


from .var import *
from .expr import *
from .func import *
import types


__all__ = ['Task']


class Task(Variable):

    __slots__ = ['_before', '_after', '_mount', '_export', '_capture']

    basetype = types.FunctionType
    empty = ''

    def __init__(self, scope=None, before=None, after=None):
        super(Task, self).__init__(scope=scope)
        self._before = set()
        self._after = set()
        if before:
            self.before(before)
        if after:
            self.after(after)
        self._mount = []
        self._export = []
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

    def dump(self, stream=None):
        function = self.get()
        print('{}=Task({}, before={}, after={})'.format(
            self.name, '<{}>'.format(function.__name__) if function else 'None',
            self._before, self._after), file=stream or sys.stdout)

    def mount(self, container, host, ro=False):
        '''Bind mount a host directory to a container directory.

        Arguments:
        container -- container directory path
        host -- host directory path, absolute or relative
        ro -- True: read-only mount, False: read-write mount
        '''
        self._mount.append((container, host, ro))

    def export(self, container, host):
        '''Export content of container directory to host directory.

        Arguments:
        container -- container directory path
        host -- host directory path, absolute or relative
        '''
        self._export.append((container, host))

    def capture(self, container):
        '''Capture container directory as task output.

        Arguments:
        container -- container directory path
        '''
        self._capture.append(container)
