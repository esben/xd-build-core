import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


from .var import *
from .expr import *
from .wrap import *
from .func import *
import copy
import types
import io


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

    def __init__(self, data=None):
        self.eval_wrapper = EvalWrapper(self)
        super(Namespace, self).__init__(data or {})

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

    def dump(self, stream=None, filter=None):
        """Dump variables in human and machine (Python) readable format.

        If given, filter must be a function taking two arguments.  It will be
        called with the variable name and value as arguments for all
        variables.  Only variables where it returns True will be included in
        the dump output.

        If stream is specified, dump will be written to the stream, and this
        method will return None.  If stream is not specified, this method will
        return the dump as a string.

        Arguments:
        stream -- output stream (default: sys.stdout)
        filter -- function taking two arguments

        """
        functions = []
        if stream is None:
            stream_ = io.StringIO()
        else:
            stream_ = stream
        for name, var in sorted(self.items()):
            if filter and not filter(name, var):
                continue
            if not var.filtered():
                continue
            if isinstance(var, Function):
                functions.append(var)
            else:
                var.dump(stream_)
        for function in functions:
            function.dump(stream_)
        if stream is None:
            return stream_.getvalue()

    def tasks(self):
        return [value for value in self.values() if isinstance(value, Task)]


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
