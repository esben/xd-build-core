import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


from .task import *


__all__ = ['Recipe']


class Recipe(object):
    """XD-build recipe."""

    def __init__(self, data):
        """Recipe constructor.

        Arguments:
        data -- Namespace instance with recipe data
        """
        self.data = data
        self.name = data['RECIPE_NAME'].get()
        self.version = data['RECIPE_VERSION'].get()
        self.type = data['RECIPE_TYPE'].get()

    def get_task(self, name):
        return Task(self, name)

    def __str__(self):
        s = '%s:%s'%(self.type, self.name)
        if self.version:
            s += '_' + self.version
        return s
