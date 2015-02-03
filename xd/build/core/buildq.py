import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

from xd.build.core.task import *
import binascii


__all__ = ['BuildQueue']


class BuildQueue(object):
    """Queue of tasks to build."""

    def __init__(self, manifest):
        """XD-build build queue constructor."""
        self.manifest = manifest
        self.targets = set()
        self.tasks = set()

    def add_task(self, task):
        if isinstance(task, list):
            for task_ in task:
                self.add_task(task_)
            return
        assert isinstance(task, Task)
        if task in self.targets:
            return
        self.targets.add(task)
        while task:
            if task in self.tasks:
                break
            self.tasks.add(task)
            log.debug('added %s', task)
            task = task.parent()

    def close(self):
        for task in self.tasks:
            task.prepare()
        done = set()
        while done != self.tasks:
            progress = False
            for task in self.tasks.difference(done):
                parent = task.parent()
                if parent and not parent in done:
                    continue
                if parent:
                    task.signature.update(parent.signature)
                log.debug('%s: %s', task, task.signature)
                done.add(task)
                progress = True
            if not progress:
                raise Exception('deadlock while calculating task signatures')

    def run_all(self):
        pending = set()
        for task in self.targets:
            while task:
                if task.isdone():
                    break
                pending.add(task)
                task = task.parent()
        while pending:
            progress = False
            for task in pending.copy():
                parent = task.parent()
                if parent and not parent.isdone():
                    continue
                task.run(self.manifest.tmpdir)
                pending.remove(task)
            
