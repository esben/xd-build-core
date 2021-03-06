import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


from .var import *
from .expr import *
from .wrap import *
import copy
import types


__all__ = ['Namespace', 'MultiBinding', 'flattened']


class MultiBinding(Exception):
    '''Variable binding to multiple names not allowed.

    For setting one (named) variable to reference the value of another (named)
    variable, you should use Expression() instead.

    Example:
        ns['FOO'] = 'foo'
        ns['ALSO_FOO'] = Expression('FOO')
    '''
    pass


class Namespace(dict):
    """XD-build data namespaces.

    Class for holding a namespace of XD-build data variables.  It is
    implemented as a mapping so it can be used as a locals to eval().
    """

    def __init__(self):
        self.eval_wrapper = EvalWrapper(self)
        super(Namespace, self).__init__(self)

    def copy(self):
        return copy.deepcopy(self)

    def __setitem__(self, key, value):
        if key in self:
            self[key].set(value)
            return
        value = wrap(value)
        if isinstance(value, Variable):
            old_name = getattr(value, 'name', None)
            if old_name is not None and old_name != key:
                raise MultiBinding('rename of Variable %s to %s not allowed'%(
                    value.name, key))
            value.name = key
        elif isinstance(value, Expression):
            pass
        else:
            raise TypeError('unsupported type for Variable %s: %s'%(
                key, type(value)))
        value.set_scope(self)
        super(Namespace, self).__setitem__(key, value)

    def __delitem__(self, key):
        var = super(Namespace, self).__getitem__(key)
        var.name = None
        super(Namespace, self).__delitem__(key)

    def eval(self, expr, g=None, wrapper=True):
        if isinstance(expr, Expression):
            expr = expr.code or expr.source
        if g is None:
            g = {}
        if wrapper:
            l = self.eval_wrapper
        else:
            l = self
        return eval(expr, g, l)


class EvalWrapper(object):

    def __init__(self, namespace):
        self.namespace = namespace

    def __getitem__(self, key):
        return self.namespace[key].get()


def flattened(namespace, filter=None):
    """Return a flat representation of a Namespace instance.

    If given, filter must be a function taking one arguments.  It will be
    called with the Variable as arguments for all variables in namespace.  It
    must return True for those variables that should be included in the
    returned dict.

    """
    d = dict()
    for name, var in namespace.items():
        if filter and not filter(var):
            continue
        if not var.filtered():
            continue
        value = var.get()
        d[name] = value
        assert type(value) in (type(None), str, list, int, float, bool, dict,
                               types.FunctionType)
    return d
