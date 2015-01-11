from xd.build.core.data.task import *
from xd.build.core.data.namespace import Namespace
from xd.build.core.data.func import Function
from xd.build.core.data.expr import Expression

import unittest
import io

def foo():
    return 'foobar'

class tests(unittest.case.TestCase):

    def setUp(self):
        self.ns = Namespace()

    def test_init_get_1(self):
        t = Task()
        self.assertIsNone(t.get())

    def test_init_get_2(self):
        self.ns['t'] = Task()
        self.assertIsNone(self.ns['t'].get())

    def test_init_get_3(self):
        self.ns['f'] = foo
        self.ns['t'] = Task()
        self.ns['t'] = self.ns['f']
        self.assertEqual(self.ns['t'].get(), foo)

    def test_init_get_4(self):
        self.ns['f'] = foo
        self.ns['t'] = Task()
        self.ns['t'] = Expression('f')
        self.assertEqual(self.ns['t'].get(), foo)

    def test_init_get_5(self):
        self.ns['f'] = foo
        self.ns['f'] = None
        self.ns['t'] = Task()
        self.ns['t'] = Expression('f')
        self.assertEqual(self.ns['t'].get(), None)

    def test_init_get_6(self):
        self.ns['t'] = Task(Expression('f'))
        self.ns['f'] = foo
        self.assertEqual(self.ns['t'].get(), foo)
        
    def test_init_invalid_1(self):
        t = Task()
        with self.assertRaises(TypeError):
            t.set(foo)

    def test_init_invalid_2(self):
        t = Task()
        with self.assertRaises(TypeError):
            t.set('foo')

    def test_init_invalid_3(self):
        t = Task()
        with self.assertRaises(TypeError):
            t.set(42)

    def test_init_invalid_4(self):
        self.ns['i'] = 42
        self.ns['t'] = Task()
        with self.assertRaises(TypeError):
            self.ns['t'] = self.ns['i']

    def test_init_invalid_5(self):
        self.ns['i'] = 42
        self.ns['i'] = None
        self.ns['t'] = Task()
        with self.assertRaises(TypeError):
            self.ns['t'] = self.ns['i']

    def test_init_after_1(self):
        self.ns['fetch'] = Task()
        self.ns['unpack'] = Task(after='fetch')
        # FIXME: check for something

    def test_after_1(self):
        self.ns['fetch'] = Task()
        self.ns['unpack'] = Task()
        self.ns['unpack'].after('fetch')

    def test_init_after_2(self):
        self.ns['fetch'] = Task()
        self.ns['unpack'] = Task(after='fetch')
        self.ns['configure'] = Task(after='unpack')
        # FIXME: check for something

    def test_after_2a(self):
        self.ns['fetch'] = Task()
        self.ns['unpack'] = Task(after='fetch')
        self.ns['configure'] = Task(after='unpack')
        self.ns['unpack'].after('fetch')
        self.ns['configure'].after(['fetch', 'unpack'])
        # FIXME: check for something

    def test_after_2b(self):
        self.ns['fetch'] = Task()
        self.ns['unpack'] = Task(after='fetch')
        self.ns['configure'] = Task(after='unpack')
        self.ns['unpack'].after('fetch')
        self.ns['configure'].after(set(['fetch', 'unpack']))
        # FIXME: check for something

    def test_init_after_3(self):
        self.ns['fetch'] = Task(after='foobar')
        # FIXME: check for something

    def test_init_before_1(self):
        self.ns['fetch'] = Task(before='unpack')
        self.ns['unpack'] = Task()
        # FIXME: check for something

    def test_before_1(self):
        self.ns['fetch'] = Task()
        self.ns['unpack'] = Task()
        self.ns['fetch'].before('unpack')
        # FIXME: check for something

    def test_init_before_2(self):
        self.ns['fetch'] = Task(before='unpack')
        self.ns['unpack'] = Task(before='configure')
        self.ns['configure'] = Task()
        # FIXME: check for something

    def test_before_2a(self):
        self.ns['fetch'] = Task(before='unpack')
        self.ns['unpack'] = Task(before='configure')
        self.ns['configure'] = Task()
        self.ns['fetch'].before('unpack')
        self.ns['configure'].before(['unpack', 'fetch'])
        # FIXME: check for something

    def test_before_2b(self):
        self.ns['fetch'] = Task(before='unpack')
        self.ns['unpack'] = Task(before='configure')
        self.ns['configure'] = Task()
        self.ns['fetch'].before('unpack')
        self.ns['configure'].before(set(['unpack', 'fetch']))
        # FIXME: check for something

    def test_init_before_3(self):
        self.ns['fetch'] = Task(before='foobar')
        # FIXME: check for something

    def test_mount_1(self):
        t = Task()
        t.mount('some/foo', '/foo')
        # FIXME: check for something

    def test_mount_2(self):
        t = Task()
        t.mount('some/foo', '/foo', True)
        # FIXME: check for something

    def test_mount_3(self):
        t = Task()
        t.mount('some/foo', '/foo', False)
        # FIXME: check for something

    def test_mount_4(self):
        t = Task()
        t.mount('some/foo', '/foo')
        t.mount('other/bar', 'bar')
        # FIXME: check for something

    def test_merge_1(self):
        t = Task()
        t.merge('/foo', 'some/foo')
        # FIXME: check for something

    def test_merge_2(self):
        t = Task()
        t.merge('/foo', 'some/foo')
        t.merge('/bar', 'other/bar')
        # FIXME: check for something

    def test_capture_1(self):
        t = Task()
        t.capture('/foo')
        # FIXME: check for something

    def test_capture_2(self):
        t = Task()
        t.capture('/foo')
        t.capture('/bar')
        # FIXME: check for something

    def test_dump_1(self):
        self.ns['t'] = Task()
        stream = io.StringIO()
        self.ns['t'].dump(stream=stream)
        self.assertEqual(stream.getvalue(),
                         't=Task(None, before=None, after=None)\n')
