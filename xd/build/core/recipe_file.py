import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


from .recipe_version import *
from .data.parser import *
from .data.namespace import *
from .data.string import *
from .data.func import *
from .recipe import *
import os
import sys
import pprint
import inspect
import ast
import astunparse


__all__ = ['RecipeFile', 'InvalidRecipeName', 'InvalidRecipeFilename']


class InvalidRecipeName(Exception):
    pass
class InvalidRecipeFilename(Exception):
    pass
class InvalidRecipeTypes(Exception):
    pass


class RecipeFile(object):
    """XD-build recipe file.

    Instances of this class represents a single XD-build recipe file.
    """

    def __init__(self, path):
        """Recipe file constructor.

        Arguments:
        path -- filename path of recipe file (must end with '.xd')
        """
        if not path.endswith('.xd'):
            raise InvalidRecipeFilename(path)
        self.path = path
        try:
            self.name, self.version = self.split_name_and_version(self.path)
        except InvalidRecipeName:
            raise InvalidRecipeFilename(path)

    @classmethod
    def split_name_and_version(cls, filename):
        """Convert recipe filename to recipe name and version number.

        Arguments:
        filename -- recipe name or filename

        Returns:
        (name, version)
        name -- recipe name (str)
        version -- recipe version (RecipeVersion instance)
        """
        if filename.endswith('.xd'):
            filename = filename[:-3]
        filename = os.path.basename(filename)
        name_and_version = filename.split('_')
        if len(name_and_version) < 1 or len(name_and_version) > 2:
            raise InvalidRecipeName(filename)
        if len(name_and_version[0]) == 0:
            raise InvalidRecipeName(filename)
        name = name_and_version[0]
        try:
            version = name_and_version[1]
        except IndexError:
            version = ''
        version = RecipeVersion(version)
        return (name, version)

    def __str__(self):
        if self.version:
            return '%s_%s'%(self.name, self.version)
        else:
            return self.name

    def __repr__(self):
        return 'RecipeFile(%r)'%(self.path)

    def __eq__(self, other):
        if not isinstance(other, RecipeFile):
            return False
        if os.path.realpath(self.path) != os.path.realpath(other.path):
            return False
        return True

    def parse(self, data, force=False):
        """Parse recipe file."""
        if not force and getattr(self, 'data', None):
            return self.data
        data = Namespace(data)
        data['RECIPE_NAME'] = self.name
        data['RECIPE_VERSION'] = String(
            str(self.version) if self.version else None)
        parser = Parser()
        self.data = parser.parse(self.path, data)
        return self.data

    def dump(self, stream=None):
        """Print entire recipe specification.

        Arguments:
        stream -- output stream (default: sys.stdout)
        """
        if stream is None:
            stream = sys.stdout
        functions = []
        for name, value in sorted(self.data.items()):
            if isinstance(value, Function):
                functions.append(value)
            else:
                value.dump(stream)
        for function in functions:
            function.dump(stream)

    def type_unfold(self):
        if 'RECIPE_TYPES' in self.data:
            recipe_types = self.data['RECIPE_TYPES'].get()
            del self.data['RECIPE_TYPES']
        else:
            recipe_types = ['machine']
        assert isinstance(recipe_types, list) and len(recipe_types) > 0
        invalid_recipe_types = [
            recipe_type for recipe_type in recipe_types
            if not recipe_type in ('native', 'machine', 'sdk',
                                   'cross', 'sdk-cross', 'canadian-cross')]
        if invalid_recipe_types:
            raise InvalidRecipeTypes(invalid_recipe_types)
        self.recipes = {}
        assert not 'RECIPE_TYPE' in self.data
        for recipe_type in recipe_types:
            recipe_data = self.data.copy()
            recipe_data['RECIPE_TYPE'] = recipe_type
            # FIXME: run type_unfold_hooks
            self.recipes[recipe_type] = Recipe(recipe_data)
        return self.recipes.values()
