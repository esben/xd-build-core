import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


__all__ = ['Target', 'InvalidTargetSpecification']


class InvalidTargetSpecification(Exception):
    pass


class Target(object):
    """XD-build target specification"""

    def __init__(self, spec):
        """Target constructor.

        The following syntaxes are supported:
        name
        name_version
        type:name
        type:name_version
        type:name:task
        type:name_version:task

        Arguments:
        spec -- Target specification string
        """
        assert isinstance(spec, str)
        parts = spec.split(':')
        if len(parts) > 3:
            raise InvalidTargetSpecification(spec)
        if len(parts) == 3:
            self.task = parts.pop()
        else:
            self.task = None
        if len(parts) == 2:
            self.type = parts.pop(0) or 'machine'
        else:
            self.type = None
        recipe = parts[0]
        if not recipe:
            raise InvalidTargetSpecification(spec)
        parts = recipe.split('_')
        if len(parts) > 2:
            raise InvalidTargetSpecification(spec)
        if len(parts) == 2:
            self.version = parts.pop()
        else:
            self.version = None
        self.name = parts[0]
        if not self.name:
            raise InvalidTargetSpecification(spec)

    def __str__(self):
        s = self.name
        if self.version is not None:
            s += '_' + self.version
        if self.type is not None:
            s = self.type + ':' + s
        if self.task is not None:
            s += ':' + self.task
        return s

    def __repr__(self):
        return 'Target({})'.format(str(self))
