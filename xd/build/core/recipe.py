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
        self.tasks = dict()

    def get_task(self, name):
        try:
            return self.tasks[name]
        except KeyError:
            task = self.tasks[name] = Task(self, name)
            return task

    def __str__(self):
        s = '%s:%s'%(self.type, self.name)
        if self.version:
            s += '_' + self.version
        return s
