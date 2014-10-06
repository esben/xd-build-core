import sys
import string
import re
import types
import collections
import copy
import json

import logging
log = logging.getLogger()


# TODO: implement dynvar handling, for correct signature generation without
# disturbance for changing DATE, TIME, MANIFEST_ORIGIN and so on.

# TODO: Implement handling of PythonExpression.cacheable, so that
# PythonExpression variables can be allowed to be cached or required to be
# kept uncacheable. Any variable that depends on one or more uncacheable
# expressions also become uncacheable.

# TODO: Ensure that lists set or added to MetaList are copied, so that they
# cannot be changed through other references, and thus circumventing the
# cache.  Same for Addition of MetaList or any other container types.

# TODO: Figure out if MetaDict and MetaDataCache is 100% safely designed,
# ie. is it possible to change cached MetaDict without invalidating the cache?


# TODO: Add method to MetaData to check if a specific variable (fx. MACHINE)
# is referenced by any (other) variable.  To do this, any variables not
# already cached needs to be dummy .get()'ed and then the cache be checked for
# any references to the variable.
#
# This method should be used for setting EXTRA_ARCH if MACHINE is referenced.
# For recipe types where MACHINE is not allowed, MACHINE should be cleaned out
# soon after recipe type is "forked".

# TODO: add MetaList.remove() and MetaList.remove_if() functions.  The removes
# should be applied in amend, after applying prepends and appends, and similar
# for *_if.  Removal of non-existant value should not cause any error, but
# just silently ignored (which is different from list.remove()).

# TODO: Add support for explicit exclusion of selected variables from
# expansion. This should be preferred in favour of legacy partial expansion,
# and perhaps even fully replace it, as it is more predictable, and allows
# proper error handling of missing variables that actually were meant to be
# defined as well as avoiding replacing variables that were really meant to be
# left in unexpanded.

# TODO: MetaInt

# TODO: MetaPythonFunc() class.  See also old MetaData.pythonfunc_init(),
# MetaData.get_pythonfunc_globals(), MetaData.get_pythonfuncs(),
# MetaData.get_pythonfunc(), MetaData.get_pythonfunc_code().

# TODO: MetaShellFunc() class

# TODO: include task (True/False) slot/attribute in python and shell func
# classes

# TODO: figure out a safe way to use PythonExpression in MetaDict keys, or add
# proper error handling on attempts to do so.

# USE flag design.
#
# (See also http://dev.gentoo.org/~ulm/pms/head/pms.html#x1-440005 for
# inspiration from gentoo project)
#
# USE flags are found in the USE MetaDict.
#     USE['nls'] = False
# Unset USE flags are None
#     USE['nls'] = None
#
# Recipes metadata marks a variable as a USE flag, fx.
#     USE['nls'] = MetaBool()
# Default value can be done by direct access to the DEFAULT_USE MetaDict
# variable.
#
# Fx.
#     USE['foobar'] = MetaString()
#     DEFAULT_USE['foobar'] = "Hello world"
#
# USE flag domains are defined by USE_DOMAINS
#     USE_DOMAINS = [ 'OVERRIDE', 'LOCAL', 'MACHINE', 'DISTRO', 'DEFAULT' ]
# When a use flag is set, fx. in a distro config file, the particular domain
# must be activated.
#     include('${DISTRO}.conf', use='DISTRO')
# causing (in the distro configuration file)
#     USE['nls'] = False
# to map to
#     DISTRO_USE['nls'] = False
# This way, copy-paste from fx. distro config to machine config, will do the
# right thing, instead of either using wrong domain or giving a parse error.
# The use flag domain is only activated as long as the file it was activated
# in is being parsed.
#
# When no domain is activated (fx. in a class or recipe file), the USE
# variable maps to USE flag declaration (as shown above).  And direct
# assignment to OVERRIDE_USE and DEFAULT_USE MetaDict variables are allowed.
#
# In all other use domains, no direct access to OVERRIDE_USE, LOCAL_USE,
# MACHINE_USE, DISTRO_USE and DEFAULT_USE is allowed.
#
# To force/set a recipe specific value for a use flag, simply do
#     OVERRIDE_USE['nls'] = True
#
# When post processing the recipe metadata, a hook must loop over all the USE
# variable keys.  For each key, if the value is None, search through the
# USE_DOMAINS defined, stopping on first matching key.  So if a domain has the
# key, and value is None, the USE flag is unset.  If the key found is not of
# the expected type, an error/exception should be raised.

# TODO: figure out required life-cycle model...  do we need to have
# pickle/unpickle for parallel parse?
#
# Metadata from bakery.conf -> oe-lite.conf -> core.oeclass
# is always parsed.
#
# A signature of resulting "raw" base metadata is needed to decide if all
# recipes needs to be reparsed, or only those that has changed input file
# mtimes.  This signature is added to the raw metadata.
#
# This raw base metadata signature should not care about dynvars, ie. all
# variables are just taken "as is" (this implies that DATE, TIME, DATETIME
# variables are not set at this point, but much later, so that it is always
# set, even when re-using cached recipe metadata).  This makes it easier to
# handle changes to manifest origin and other dynvars, requring full reparse
# when they are changed.
#
# Setting of DATETIME variable should be moved to datetime.oeclass file, and
# explicitly inherited only by those classes/recipes that really need it.
# This class should setup a hook to set DATE, TIME and DATETIME to common
# values for all recipes, but after caching is resolved, so that all recipes
# get the same values, no matter if they were reparsed or read from cache.
#
# Signature of imported environment variables must also be included in this
# raw base metadata and thus the signature of it.
#
# As needed, the recipes are parsed, each recipe in a separate process.  The
# metadata does therefore not need to be copied.  When done, a signature of
# the resulting recipe metadata is calculated and inserted into the recipe
# metadata.  The recipe metadata is then serialized into a disk file,
# preferably JSON format or other human readable format for easier debugging.
# If needed (hopefully not, but likely), a special summary of the recipe
# metadata must be written to a separate file, including all the information
# needed to create the cookbook.
#
# Back in the main process, the recipe metadata (or just the summary, if it is
# implemented) is read in for all recipes, and used to create the cookbook.
#
# After the runq is created from the cookbook, all tasks included in the build
# are read in from cache (JSON) files, if recipe metadata signature (or token)
# in the file is identical to the recipe metadata.  If cache is invalid, a
# process is created for each task, and this process finalizes the task
# metadata (flattening it to FlatMetaData, collapsing all appends, prepends,
# updates, override_if, and so on, removing all unneeded variables (according
# to .emit and .omit attributes and such).  The signature of the resulting
# FlatMetaData is calculated, and this is written to a cache file (JSON)
# together with the task metadata.
#
# For improved debugging support, it would be nice if each variable could be
# given a signature, so that we can pinpoints exactly what has changed to
# cause a task to be rebuilt.
#
# USE flag force/mask idea inspired from gentoo.  Allow profiles (including
# recipe profile) to require specific USE flag values.  So a recipe could
# fx. require systemd=True, or foobar=42, and when fx. a distro (or another
# active profile) does not set fulfil that requirement, the recipe is not
# valid (cannot be built).  But instead of force/mask, we should use Python
# eval blocks, so that you can require things like 'foo <= 42' and 'foo == 42
# or bar > 10' and "foobar.startswith('hello')"
#
# See also http://dev.gentoo.org/~ulm/pms/2/pms.pdf


# TODO: When a mtime difference for a recipe is detected, the recipe metadata
# will be reparsed.  Back in the baker process, the (re)parsed metdata is
# compared to the previous metadata (if available, loading it from old cache
# file), and based on metadata signature being changed, decide if the old
# (task) cache can still be used, or if we have to regenerate that.
#
# Also, when metadata is different, add a manifest command for telling which
# variables have changed in a specific recipe (or task?) metadata since last
# time.  Optionally, allowing to specify a specific metadata dump dir.  Add a
# manifest command for generating a new metadata dump/cache dir for later
# comparision.
#

# TODO: test if builtin filter() can be used for efficient retrieving list of
# variables with a specific attribute set (True).

# TODO: Reimplement MetaData.import_env as method in some other module, as it
# is not logically part of the MetaData abstraction.

# TODO: add_hook() method

# TODO: Add API and internal documentation to all classes, attributes and
# methods!


import hashlib
import pprint

class MetaHasher(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self.m = hashlib.md5()

    def update_raw(self, value):
        #print(value, end='')
        assert isinstance(value, str)
        self.m.update(value.encode('utf-8'))

    def update(self, value):
        if isinstance(value, dict):
            self.update_raw(pprint.pformat(self.hash_repr(value)))
        else:
            self.update_raw(repr(self.hash_repr(value)))

    @staticmethod
    def hash_repr(value):
        if isinstance(value, str):
            return value.encode('utf-8')
        elif type(value) == dict:
            return dict([(
                        (str(k_v[0]) if isinstance(k_v[0], str) else k_v[0]),k_v[1]) for k_v in list(value.items())])
        elif type(value) in (int, float, str, dict, list,
                             PythonExpression):
            return value
        elif isinstance(value, MetaVar):
            return value.signature()
        else:
            raise TypeError("cannot hash %s value: %s"%(
                    type(value).__name__, value))

    def __repr__(self):
        return "s'%s'"%(self.m.hexdigest())

    def __str__(self):
        return self.m.hexdigest()

    def __eq__(self, other):
        if isinstance(other, MetaHasher):
            return self.m.digest() == other.m.digest()
        elif isinstance(other, str):
            return self.m.hexdigest() == other
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


def all_slots(cls):
    slots = set(getattr(cls, '__slots__', []))
    for base in cls.__bases__:
        slots.update(all_slots(base))
    return slots


def hash_slots(cls):
    slots = set(getattr(cls, '__slots__', [])).difference(
        getattr(cls, 'nohash_slots', []))
    for base in cls.__bases__:
        slots.update(hash_slots(base))
    return slots


class MetaDataRecursiveEval(Exception):
    pass

class MetaDataDuplicateDictKey(Exception):
    pass


class MetaDataStack(object):

    __slots__ = [ 'var', 'deps', 'scope' ]

    def __init__(self, scope):
        self.scope = scope
        self.var = []
        self.deps = []

    # self.var[-1] is the currently-being-evaluated variable

    # self.deps[-1] is list of variables that the currently-being-evaluated
    # variable depends on.  If variable is a string, the variable is
    # undefined, and should be registered with MetaData.watchers.

    def __str__(self, prefix='\n  '):
        return prefix.join(self.var)

    def push(self, var):
        assert isinstance(var, MetaVar)
        if var in self.var:
            raise MetaDataRecursiveEval(
                '%s->%s'%('->'.join([v.name for v in self.var]), var.name))
        self.var.append(var)
        self.deps.append(set())

    def pop(self):
        var = self.var.pop()
        deps = self.deps.pop()
        if self.var:
            self.deps[-1].add(var)
            self.deps[-1].update(deps)
        return deps

    def add_dep(self, var):
        if not self.deps:
            return
        if isinstance(var, str):
            try:
                var = self.scope[var]
            except KeyError:
                pass
        self.deps[-1].add(var)

    def add_deps(self, deps):
        if self.deps and deps:
            self.deps[-1].update(deps)

    def clear_deps(self):
        self.deps[-1] = set()


class MetaData(dict):

    __slots__ = [ 'stack', 'watchers' ]

    def __init__(self, init=None):
        dict.__init__(self)
        self.watchers = {}
        if init is None:
            self.stack = MetaDataStack(self)
            MetaList(self, 'OVERRIDES', [])
        elif isinstance(init, MetaData):
            for name,var in init.items():
                var.copy(self)
            self.stack = MetaDataStack(self)
        elif isinstance(init, dict):
            self.stack = MetaDataStack(self)
            for name,var in init.items():
                MetaVar(self, name, var)
            if not 'OVERRIDES' in self:
                MetaList(self, 'OVERRIDES', [])

    def __setitem__(self, key, val):
        # FIXME: remove this assert when/if dot notation is droppped
        assert not '.' in key
        if self.__contains__(key):
            self[key].set(val)
            return
        if type(val) in (str, str, list, dict, int, int, bool):
            MetaVar(self, key, val)
        elif not isinstance(val, MetaVar):
            raise TypeError('cannot assign %s to MetaData'%(type(val)))
        else:
            val.name = key
            dict.__setitem__(self, key, val)
        # Invalidate any variables with watchers on this variable (name),
        # ie. variables that have cached values depending on the non-existance
        # of this variable.
        for var in list(self.watchers.get(key, [])):
            var.cache_invalidate()

    def __getitem__(self, key):
        var = dict.__getitem__(self, key)
        return var

    def __delitem__(self, key):
        var = dict.__getitem__(self, key)
        var.cache_invalidate()
        var.name = None
        dict.__delitem__(self, key)

    def expand_full(self, value):
        if not isinstance(value, str):
            return value
        def expand(sub):
            sub = sub.group(0)
            name = sub[2:-1]
            var = dict.__getitem__(self, name)
            value = var.get()
            if not isinstance(value, str):
                raise TypeError(
                    "expanded variables must be string: %s is %s"%(
                        name, type(value)))
            return value
        return re.sub(self.expand_re, expand, value)

    def expand_partial(self, value):
        # FIXME: add support for partial expand of MetaDict values
        #if not isinstance(value, basestring):
        #    return value
        def expand(sub):
            sub = sub.group(0)
            name = sub[2:-1]
            try:
                var = dict.__getitem__(self, name)
            except KeyError:
                self.stack.add_dep(name)
                return sub
            value = var.get()
            if not isinstance(value, str):
                raise TypeError(
                    "expanded variables must be string: %s is %s"%(
                        name, type(value)))
            return value
        return re.sub(self.expand_re, expand, value)

    def expand_clean(self, value):
        # FIXME: add support for clean expand of MetaDict values
        #if not isinstance(value, basestring):
        #    return value
        def expand(sub):
            sub = sub.group(0)
            name = sub[2:-1]
            try:
                var = dict.__getitem__(self, name)
            except KeyError:
                self.stack.add_dep(name)
                return ''
            value = var.get()
            if not isinstance(value, str):
                raise TypeError(
                    "expanded variables must be string: %s is %s"%(
                        name, type(value)))
            return value
        return re.sub(self.expand_re, expand, value)

    expand_re = re.compile(r'\$\{[a-zA-Z_]+\}')
    def expand(self, value, method='full'):
        if method == 'no':
            return value
        elif method == 'full':
            expand = self.expand_full
        elif method == 'partial':
            expand = self.expand_partial
        elif method == 'clean':
            expand = self.expand_clean
        else:
            raise TypeError('invalid expand method: %r'%(method))
        if isinstance(value, str):
            return expand(value)
        elif isinstance(value, list):
            return list(map(expand, value))
        else:
            return value

    def eval(self, value):
        if isinstance(value, PythonExpression):
            value = eval(value.code, {}, self)
        if isinstance(value, MetaVar):
            value = value.get()
        if isinstance(value, dict):
            expanded = {}
            for key, val in value.items():
                key = self.expand(self.eval(key))
                if key in expanded:
                    raise MetaDataDuplicateDictKey(key)
                expanded[key] = self.expand(self.eval(val))
            value = expanded
        return value

    def __repr__(self):
        return "%s()"%(self.__class__.__name__)

    def flattened(self):
        d = {}
        for name, var in self.items():
            if name == 'OVERRIDES':
                continue
            d[name] = var.get()
        return d

    def is_solitary(self, var):
        if isinstance(var, str):
            return self.is_solitary(self[var])
        assert isinstance(var.name, str) and not '.' in var
        assert var.scope == self
        self.cache_all()
        for other in list(self.values()):
            if other == var:
                continue
            #if other.cache and var in other.cache[1]:
            if var in other.cache[1]:
                return False
        try:
            watchers = self.watchers[var.name]
        except KeyError:
            pass
        else:
            if watchers:
                return False
        return True

    def cache_all(self):
        for name, var in self.items():
            if not var.cache:
                var.get()

    def __eq__(self, other):
        if isinstance(other, MetaData):
            return self.signature() == other.signature()
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def signature(self, t=str, dynvars=[]):
        if t == str:
            m = hashlib.md5()
            for name,var in sorted(iter(self.items()), key=lambda x: x[0]):
                # FIXME: skip if name is in dynvars
                m.update(('%s:%s\n'%(name, var.signature(dynvars=dynvars)))
                         .encode('utf-8'))
            m = m.hexdigest()
        elif t == dict:
            m = {}
            for name,var in self.items():
                m[str(name)] = var.signature(dynvars=dynvars)
        else:
            raise TypeError("invalid type argument t: %s"%(t))
        return m

    def dumps(self, *args, **kwargs):
        obj = {
            '__jsonclass__': [self.__class__.__name__],
            'dict': dict(self),
        }
        kwargs['default'] = MetaVar.json_encode
        return json.dumps(obj, *args, **kwargs)

    @staticmethod
    def loads(s, *args, **kwargs):
        d = MetaData()
        kwargs['object_hook'] = d.json_decode
        return json.loads(s, *args, **kwargs)

    def json_decode(self, obj):
        try:
            cls = obj.pop('__jsonclass__')
        except KeyError:
            return obj
        constructor = eval(cls[0])
        try:
            args = cls[1]
        except IndexError:
            args = []
        try:
            kwargs = cls[2]
        except IndexError:
            kwargs = {}
        if issubclass(constructor, MetaVar):
            instance_name = name = obj.pop('name')
            instance = constructor(self, name, *args, **kwargs)
        elif issubclass(constructor, MetaData):
            # Update (replace) the MetaData dict with the decoded variables
            assert len(self) == len(obj['dict'])
            dict.update(self, obj['dict'])
            assert len(self) == len(obj['dict'])
            del obj['dict']
            instance = self
        else:
            instance = constructor(*args, **kwargs)
        for name, value in obj.items():
            setattr(instance, name, value)
        return instance

    def print(self, details=False, sep=None, file=sys.stdout):
        if sep is None:
            sep = '\n' if details else ''
        names = sorted(self.keys())
        while names:
            name = names.pop()
            var = self[name]
            value = repr(var.get())
            if details:
                source = var.get(evaluate=False)
                if source != value:
                    file.write("# %s = %s\n"%(name, source))
            file.write("%s = %s%s\n"%(name, value, sep if names else ''))


class MetaVar(object):

    __slots__ = [ 'scope', 'name', 'value', 'override_if', 'emit', 'omit',
                  'cache', 'watchers' ]
    nohash_slots = [ 'scope', 'cache', 'watchers' ]

    fixup_types = []

    def __new__(cls, scope, name=None, value=None):
        if cls != MetaVar:
            return super(MetaVar, cls).__new__(cls)
        if isinstance(value, MetaVar):
            return super(MetaVar, cls).__new__(type(value))
        elif isinstance(value, str):
            return super(MetaVar, cls).__new__(MetaString)
        elif isinstance(value, list):
            return super(MetaVar, cls).__new__(MetaList)
        elif isinstance(value, dict):
            return super(MetaVar, cls).__new__(MetaDict)
        elif isinstance(value, bool):
            return super(MetaVar, cls).__new__(MetaBool)
        elif isinstance(value, int):
            return super(MetaVar, cls).__new__(MetaInt)
        else:
            return super(MetaVar, cls).__new__(MetaString)

    def __init__(self, scope, name=None, value=None):
        assert isinstance(scope, MetaData)
        assert (value is None or
                isinstance(value, self.basetype) or
                isinstance(value, type(self)) or
                isinstance(value, PythonExpression))
        self.scope = scope
        self.cache = None
        self.watchers = set()
        if isinstance(value, MetaVar):
            self.scope = scope
            for attr in all_slots(self.__class__):
                if attr in ('scope', 'name', 'cache', 'watchers'):
                    continue
                try:
                    attr_val = getattr(value, attr)
                    if isinstance(attr_val, OverrideDict):
                        attr_val = attr_val.copy()
                        attr_val.var = self
                    elif isinstance(attr_val, collections.Container):
                        attr_val = copy.deepcopy(attr_val)
                    setattr(self, attr, attr_val)
                except AttributeError:
                    pass
        else:
            self.value = value
        self.name = name
        self.override_if = OverrideDict()
        if name is not None and not '.' in name:
            self.scope[name] = self

    def copy(self, scope=None):
        if scope is None:
            return self.__class__(self.scope, None, self)
        else:
            return self.__class__(scope, self.name, self)

    def __setattr__(self, name, value):
        if name in ('override_if', 'prepend_if', 'append_if', 'update_if'):
            value.var = self
        object.__setattr__(self, name, value)

    def __str__(self):
        return str(self.get())

    def set(self, value):
        if isinstance(value, MetaVar):
            value = value.get()
        if not (isinstance(value, self.basetype) or
                self.is_fixup_type(value) or
                value is None or
                isinstance(value, PythonExpression)):
            raise TypeError("cannot set %r to %s value"%(
                    self, type(value).__name__))
        self.cache_invalidate()
        self.value = value

    def weak_set(self, value):
        if self.value is None:
            self.cache_invalidate()
            return self.set(value)

    def is_fixup_type(self, value):
        for fixup_type in self.fixup_types:
            if isinstance(value, fixup_type):
                return True
        return False

    # Format of MetaVar.cache attribute: (value, deps)

    def get(self, evaluate=True):
        assert isinstance(evaluate, bool)
        if evaluate:
            try:
                value = self.cache[0]
            except:
                self.scope.stack.push(self)
            else:
                self.scope.stack.add_dep(self)
                self.scope.stack.add_deps(self.cache[1])
                return value
        try:
            if evaluate:
                value = self.scope.eval(self.value)
                if self.is_fixup_type(value):
                    value = self.fixup(value)
                if not (isinstance(value, self.basetype) or
                        value is None):
                    raise TypeError("invalid type in %s %s value: %s"%(
                            type(self).__name__, self.name,
                            type(value).__name__))
            else:
                if self.value is None:
                    value = []
                else:
                    value = [self.value]
            if isinstance(self, MetaSequence):
                value = self.amend(value, evaluate)
            if self.override_if:
                for override in self.scope['OVERRIDES']:
                    if override in self.override_if:
                        if evaluate:
                            self.scope.stack.clear_deps()
                            value = self.scope.eval(self.override_if[override])
                            if not (isinstance(value, self.basetype) or
                                    value is None):
                                raise TypeError(
                                    "invalid type in %s %s override: %s"%(
                                        type(self).__name__, self.name,
                                        type(value).__name__))
                        else:
                            if self.override_if[override] is None:
                                value = []
                            else:
                                value = [self.override_if[override]]
                        break
                if evaluate:
                    self.scope.stack.add_dep('OVERRIDES')
            if isinstance(self, MetaSequence):
                value = self.amend_if(value, evaluate)
            if isinstance(value, str) and evaluate:
                value = self.scope.expand(value, method=self.expand)
            if evaluate:
                self.cache_value(value)
        finally:
            if evaluate:
                self.scope.stack.pop()
        if not evaluate:
            if not value:
                return None
            value = [v for v in value if v is not None]
            value = [str(v) if isinstance(v, PythonExpression)
                else repr(v) for v in value]
            value = ' + '.join(value)
        return value

    def cache_value(self, value):
        self.cache = (value, self.scope.stack.deps[-1])
        for var in self.cache[1]:
            if isinstance(var, MetaVar):
                var.watchers.add(self)
            else:
                assert isinstance(var, str)
                if var in self.scope.watchers:
                    self.scope.watchers[var].add(self)
                else:
                    self.scope.watchers[var] = set([self])

    def cache_invalidate(self, recurse=True):
        # Loop over list of variables that depends on this variable (this list
        # is updated by the variables that depend on this variable as they are
        # storing their own cached value), and invalidate their cache
        # information.
        if recurse:
            for var in list(self.watchers):
                var.cache_invalidate(recurse=False)
        # Clear any watchers information registered by this variable
        if not self.cache:
            return
        for var in self.cache[1]:
            if isinstance(var, str):
                self.scope.watchers[var].remove(self)
            else:
                var.watchers.remove(self)
        # And clear the cached value and it's dependency information
        self.cache = None

    def signature(self, m=None, dynvars=[]):
        if m is None:
            m = MetaHasher()
        m.update_raw(self.__class__.__name__ + '\n')
        for slot in sorted(hash_slots(self.__class__)):
            value = getattr(self, slot, None)
            if value is None:
                continue
            if isinstance(value, OverrideDict) and not value:
                continue
            # FIXME: skip empty appends/prepends if it improves performance
            m.update_raw(slot + ':')
            if isinstance(value, list):
                m.update(list(map(m.hash_repr, value)))
            elif isinstance(value, dict):
                m.update(dict([(e[0], m.hash_repr(e[1])) for e in iter(value.items())]))
            else:
                m.update(value)
            m.update_raw('\n')
        return m

    @staticmethod
    def json_encode(var):
        assert isinstance(var, MetaVar)
        return var.json_obj()

    def json_obj(self):
        import inspect
        slots = set()
        for cls in inspect.getmro(self.__class__):
            try:
                slots.update(cls.__slots__)
            except AttributeError:
                pass
        obj = { '__jsonclass__': [self.__class__.__name__] }
        for slot in slots:
            if slot == 'scope':
                continue
            try:
                attr = getattr(self, slot)
                if isinstance(attr, OverrideDict):
                    obj[slot] = attr.json_obj()
                elif type(attr) in (str, str, int, int, float, bool,
                                    type(None), list, dict):
                    obj[slot] = attr
            except AttributeError:
                pass
        return obj


class OverrideDict(dict):

    __slots__ = [ 'dict', 'var' ]

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __setitem__(self, key, value):
        if isinstance(value, MetaVar):
            value = value.get()
        if not (value is None or
                isinstance(value, self.var.basetype) or
                isinstance(value, PythonExpression) or
                self.var.is_fixup_type(value)):
            raise TypeError("cannot set %r override to %s value"%(
                    self.var.name or type(self.var).__name__,
                    type(value).__name__))
        self.var.cache_invalidate()
        dict.__setitem__(self, key, value)

    def json_obj(self):
        return { '__jsonclass__': [self.__class__.__name__, [self]] }


class MetaSequence(MetaVar):

    __slots__ = [ 'prepends', 'appends',
                  'prepend_if', 'append_if' ]

    def __init__(self, scope, name=None, value=None):
        if isinstance(value, MetaVar):
            for attr in MetaSequence.__slots__:
                setattr(self, attr, getattr(value, attr))
        else:
            self.prepends = []
            self.prepend_if = OverrideDict()
            self.appends = []
            self.append_if = OverrideDict()
        super(MetaSequence, self).__init__(scope, name, value)

    def __getitem__(self, index):
        return self.get().__getitem__(index)

    def __len__(self):
        return self.get().__len__()

    def __contains__(self, item):
        return self.get().__contains__(item)

    def index(self, sub, start=0, end=None):
        if end is None:
            return self.get().index(sub, start)
        else:
            return self.get().index(sub, start, end)

    def count(self, sub):
        return self.get().count(sub)

    def prepend(self, value):
        if isinstance(value, MetaVar):
            value = value.get()
        if not (isinstance(value, self.basetype) or
                self.is_fixup_type(value) or
                value is None or
                isinstance(value, PythonExpression)):
            raise TypeError('cannot prepend %s to %s'%(type(value), type(self)))
        self.cache_invalidate()
        self.prepends.append(value)

    def append(self, value):
        if isinstance(value, MetaVar):
            value = value.get()
        if not (isinstance(value, self.basetype) or
                self.is_fixup_type(value) or
                value is None or
                isinstance(value, PythonExpression)):
            raise TypeError('cannot append %s to %s'%(type(value), type(self)))
        self.cache_invalidate()
        self.appends.append(value)

    def __add__(self, other):
        if not (isinstance(other, type(self)) or
                  isinstance(other, self.basetype)):
            raise TypeError(
                "cannot concatenate %s and %s objects"%(
                    type(self), type(other)))
        #value = self.__class__(self.scope)
        #self.scope.stack.push(value)
        #value.set(self.get())
        #if isinstance(other, MetaVar):
        #    other = other.get()
        #if other:
        #    value.append(other)
        #self.scope.stack.pop()
        #return value
        value = self.copy()
        self.scope.stack.push(value)
        self.scope.stack.add_dep(self)
        if isinstance(other, MetaVar):
            self.scope.stack.add_dep(other)
        value.append(other)
        self.scope.stack.pop()
        return value

    def set(self, value):
        super(MetaSequence, self).set(value)
        self.prepends = []
        self.appends = []

    def weak_set(self, value):
        if self.value is None and not self.prepends and not self.appends:
            self.cache_invalidate()
            return self.set(value)

    def amend_prepend(self, value, amend_value, evaluate):
        if evaluate:
            amend_value = self.scope.eval(amend_value)
        if amend_value is None:
            return value
        if value is None:
            value = self.empty
        if evaluate:
            if isinstance(amend_value, self.basetype):
                value = amend_value + value
            elif self.is_fixup_type(amend_value):
                value = self.fixup(amend_value) + value
            else:
                raise TypeError(
                    "unsupported prepend operation: %s to %s"%(
                        type(amend_value), type(value)))
        else:
            value = [amend_value] + value
        return value

    def amend_append(self, value, amend_value, evaluate):
        if evaluate:
            amend_value = self.scope.eval(amend_value)
        if amend_value is None:
            return value
        if value is None:
            value = self.empty
        if evaluate:
            if isinstance(amend_value, self.basetype):
                value = value + amend_value
            elif self.is_fixup_type(amend_value):
                value = value + self.fixup(amend_value)
            else:
                raise TypeError(
                    "unsupported append operation: %s to %s"%(
                        type(amend_value), type(value)))
        else:
            value = value + [amend_value]
        return value

    def amend(self, value, evaluate):
        if self.prepends:
            for amend_value in self.prepends:
                value = self.amend_prepend(value, amend_value, evaluate)
        if self.appends:
            for amend_value in self.appends:
                value = self.amend_append(value, amend_value, evaluate)
        return value

    def amend_if(self, value, evaluate):
        value = copy.copy(value)
        if self.prepend_if:
            self.scope.stack.add_dep('OVERRIDES')
            for override in self.scope['OVERRIDES']:
                if override in self.prepend_if:
                    value = self.amend_prepend(value, self.prepend_if[override],
                                               evaluate)
        if self.append_if:
            self.scope.stack.add_dep('OVERRIDES')
            for override in self.scope['OVERRIDES']:
                if override in self.append_if:
                    value = self.amend_append(value, self.append_if[override],
                                              evaluate)
        return value


class MetaString(MetaSequence):

    __slots__ = [ 'expand', 'export' ]

    basetype = str
    empty = ''

    def __init__(self, scope, name=None, value=None):
        if isinstance(value, MetaVar):
            for attr in MetaString.__slots__:
                try:
                    setattr(self, attr, getattr(value, attr))
                except AttributeError:
                    pass
        else:
            self.expand = 'full'
        super(MetaString, self).__init__(scope, name, value)

    def __str__(self):
        return self.get()

    def count(self, sub, start=None, end=None):
        return self.get().count(sub, start, end)


class MetaList(MetaSequence):

    __slots__ = [ 'separator', 'separator_pattern', 'expand' ]

    basetype = list
    empty = []
    fixup_types = [ str ]

    def __init__(self, scope, name=None, value=None):
        if isinstance(value, MetaVar):
            for attr in MetaString.__slots__:
                try:
                    setattr(self, attr, getattr(value, attr))
                except AttributeError:
                    pass
        else:
            self.expand = 'full'
        super(MetaList, self).__init__(scope, name, value)

    def __iter__(self):
        return self.get().__iter__()

    def __reversed__(self):
        return self.get().__reversed__()

    def __str__(self):
        value = self.get()
        separator = getattr(self, 'separator', ' ')
        if separator is not None:
            return separator.join(value)
        else:
            return str(value)

    def fixup(self, value):
        value = self.scope.expand(value, method=self.expand)
        separator_pattern = getattr(self, 'separator_pattern', '[ \t\n]+')
        value = re.split(separator_pattern, value)
        if value[0] == '':
            value = value[1:]
        if value[-1] == '':
            value = value[:-1]
        return value

    def amend(self, value, evaluate):
        return super(MetaList, self).amend(copy.copy(value), evaluate)

    def amend_if(self, value, evaluate):
        return super(MetaList, self).amend_if(copy.copy(value), evaluate)

    def __add__(self, other):
        value = self.get()
        if not (isinstance(other, type(self)) or
                isinstance(other, MetaString) or
                self.is_fixup_type(other) or
                isinstance(other, self.basetype)):
            raise TypeError(
                "cannot concatenate %s and %s objects"%(
                    type(self), type(other)))
        value = self.copy()
        value.append(other)
        return MetaVar(self.scope, value=value)


class MetaDict(MetaVar):

    __slots__ = [ 'updates', 'update_if', 'expand' ]
    basetype = dict
    empty = {}

    def __init__(self, parent, name=None, value=None):
        assert isinstance(parent, MetaData) or isinstance(parent, MetaDict)
        assert (value is None or
                isinstance(value, MetaDict) or
                isinstance(value, dict))
        self.updates = []
        self.update_if = OverrideDict()
        if isinstance(parent, MetaData):
            self.scope = parent
        else:
            self.scope = parent.scope
            name = '%s.%s'%(parent.name, name)
        super(MetaDict, self).__init__(self.scope, name, {})
        if isinstance(value, dict):
            for key, val in value.items():
                self[key] = val
            return
        else:
            self.expand = 'full'

    def __setitem__(self, key, val):
        if self.value is None:
            self.value = {}
        if self.value.__contains__(key):
            self.value[key].set(val)
            return
        if isinstance(val, dict):
            var = MetaVar(self, key, val)
        else:
            name = '%s.%s'%(self.name, key)
            if type(val) in (str, str, list, int, int, bool):
                var = MetaVar(self.scope, name, val)
            elif isinstance(val, MetaVar):
                var = val
                var.name = name
            else:
                raise TypeError("cannot assign %s value to MetaDict"%(
                        type(val)))
        self.value[key] = var

    def __getitem__(self, key):
        return self.value[key]

    def __delitem__(self, key):
        if self.value is None:
            raise KeyError(key)
        del self.value[key]

    def __len__(self):
        value = self.get()
        if not value:
            return 0
        else:
            return value.__len__()

    def __contains__(self, key):
        value = self.get()
        if not value:
            return False
        else:
            return self.get().__contains__(key)

    def __iter__(self):
        return self.get().__iter__()

    def set(self, value):
        super(MetaDict, self).set(value)
        self.updates = []

    def weak_set(self, value):
        if self.value is None and not self.updates:
            self.cache_invalidate()
            return self.set(value)

    def get(self, evaluate=True):
        if evaluate:
            if self.cache:
                value, deps = self.cache
                self.scope.stack.add_dep(self)
                self.scope.stack.add_deps(deps)
                return value
            else:
                self.scope.stack.push(self)
        try:
            if evaluate:
                value = self.scope.eval(self.value)
                if not (isinstance(value, self.basetype) or
                        value is None):
                    raise TypeError("invalid type in %s %s value: %s"%(
                            type(self).__name__, self.name,
                            type(value).__name__))
            else:
                if self.value is None:
                    value = []
                else:
                    value = [self.value]
            value = self.amend(value, evaluate)
            if self.override_if:
                for override in self.scope['OVERRIDES']:
                    if override in self.override_if:
                        if evaluate:
                            self.scope.stack.clear_deps()
                            value = self.scope.eval(self.override_if[override])
                            if not (isinstance(value, self.basetype) or
                                    value is None):
                                raise TypeError(
                                    "invalid type in %s %s override: %s"%(
                                        type(self).__name__, self.name,
                                        type(value).__name__))
                        else:
                            if self.override_if[override] is None:
                                value = []
                            else:
                                value = [self.override_if[override]]
                        break
                if evaluate:
                    self.scope.stack.add_dep('OVERRIDES')
            value = self.amend_if(value, evaluate)
            if evaluate:
                self.cache_value(value)
        finally:
            if evaluate:
                self.scope.stack.pop()
        if not evaluate:
            if not value:
                return None
            value = ' + '.join([str(v) if isinstance(v, PythonExpression)
                    else repr(v) for v in value])
        return value

    def items(self):
        value = self.get()
        if not value:
            return []
        else:
            return list(value.items())

    def keys(self):
        value = self.get()
        if not value:
            return []
        else:
            return list(value.keys())

    def update(self, *args, **kwargs):
        for value in args:
            if isinstance(value, MetaVar):
                value = value.get()
            if value is None:
                pass
            elif isinstance(value, PythonExpression):
                self.updates.append(value)
            elif isinstance(value, self.basetype):
                self.updates.append(value)
            else:
                raise TypeError('cannot update %s with %s'%(
                        type(self), type(value)))
        if kwargs:
            value = {}
            for key, val in kwargs.items():
                value[key] = self.scope.eval(val)
            self.updates.append(value)

    def amend_update(self, value, amend_value, evaluate):
        if evaluate:
            amend_value = self.scope.eval(amend_value)
        if not amend_value:
            return value
        if value is None:
            value = self.empty
        if evaluate:
            if isinstance(amend_value, self.basetype):
                value.update(amend_value)
            else:
                raise TypeError(
                    "unsupported update_if operation: %s to %s"%(
                        type(amend_value), type(value)))
        else:
            value = value + [amend_value]
        return value

    def amend(self, value, evaluate):
        if self.updates:
            for amend_value in self.updates:
                value = self.amend_update(value, amend_value, evaluate)
        return value

    def amend_if(self, value, evaluate):
        if self.update_if:
            self.scope.stack.add_dep('OVERRIDES')
            for override in reversed(self.scope['OVERRIDES']):
                if override in self.update_if:
                    value = self.amend_update(value, self.update_if[override],
                                              evaluate)
        return value


class MetaBool(MetaVar):

    __slots__ = []
    basetype = bool


class MetaInt(MetaVar):

    __slots__ = []
    basetype = int


class PythonExpression(object):

    __slots__ = [ 'source', 'filename', 'lineno', 'code', 'cacheable' ]

    def __init__(self, source, filename=None, lineno=0, cacheable=True):
        assert isinstance(source, str)
        self.source = source
        if lineno != 0:
            source = '\n'*lineno + source
        self.filename = filename
        self.code = compile(source, filename or '<unknown>', 'eval')
        self.cacheable = cacheable

    def __repr__(self):
        return 'PythonExpression(%r)'%(self.source)

    def __str__(self):
        return self.source
