import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


from .var import *
from .expr import *
from .func import *
import types


__all__ = ['Task']


class Task(Variable):

    basetype = types.FunctionType
    empty = ''

    def __init__(self, scope=None):
        super(Task, self).__init__(scope=scope)

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

