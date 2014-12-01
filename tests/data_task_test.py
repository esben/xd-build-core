from xd.build.core.data.task import *
from xd.build.core.data.namespace import Namespace
from xd.build.core.data.func import Function
from xd.build.core.data.expr import Expression

import unittest

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

