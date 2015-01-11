import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

from xd.build.core.recipe_file import *


__all__ = ['Cookbook']


class Cookbook(object):
    """Collection of XD-build recipes."""

    def __init__(self, recipe_files=None):
        """XD-build cookbook constructor.

        Arguments:
        recipe_files -- A list of RecipeFile's to include in cookbook
        """
        self.recipe_files = []
        self.recipes = []
        self.add(recipe_files)

    def add(self, recipe_file):
        if not recipe_file:
            return
        elif isinstance(recipe_file, list):
            for recipe_file in recipe_file:
                self.add(recipe_file)
        else:
            assert isinstance(recipe_file, RecipeFile)
            self.recipe_files.append(recipe_file)

    def parse(self, data=None, force=False):
        """Parse all recipe files.

        Arguments:
        data -- initial recipe data variables
        force -- True: force (re)parse of all recipes, False: skip already
                 parsed recipes.
        """
        for recipe_file in self.recipe_files:
            recipe_file.parse(data)
            self.recipes.extend(recipe_file.type_unfold())

    def get_task(self, target):
        candidates = [recipe for recipe in self.recipes
                      if (recipe.name == target.name
                          and recipe.type == target.type)]
        if target.version is None:
            candidates.sort(key=lambda r: r.version, reverse=True)
        else:
            candidates = [recipe for recipe in candidates
                          if recipe.version == target.version]
        recipe = candidates[0]
        return recipe.get_task(target.task)
