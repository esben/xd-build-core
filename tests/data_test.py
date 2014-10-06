from data.data import *

import unittest


#class TestCase(unittest.TestCase):
#
#    def setUp(self):
#        self.addTypeEqualityFunc(MetaData, self.assertMetaDataEqual)
#
#    def assertMetaDataEqual(self, x, y, msg=None):
#        print('foobar')
#        if x.signature() == y.signature():
#            return True
#        else:
#            # FIXME: add detailed signature diff information to msg
#            raise self.failureException(msg)


class TestMetaData(unittest.TestCase):

    def setUp(self):
        pass

    def test_init_default(self):
        d = MetaData()
        self.assertIsInstance(d, MetaData)

    def test_str(self):
        d = MetaData()
        self.assertIsInstance(str(d), str)

    def test_stack_str(self):
        d = MetaData()
        self.assertEqual(str(d.stack), '')

    def test_init_metadata(self):
        src = MetaData()
        MetaVar(src, 'FOO', 'foo')
        self.assertEqual(src['FOO'].get(), 'foo')
        dst = MetaData(src)
        self.assertIsInstance(dst, MetaData)
        src['FOO'].set('bar')
        self.assertEqual(dst['FOO'].get(), 'foo')

    def test_init_dict(self):
        d = MetaData({'FOO': 'foo', 'BAR': 'bar'})
        self.assertEqual(d['FOO'].get(), 'foo')
        d['FOO'].set('bar')
        self.assertEqual(d['FOO'].get(), 'bar')

    def test_set_str(self):
        d = MetaData()
        d['FOO'] = 'foo'
        self.assertIsInstance(d['FOO'], MetaString)
        self.assertEqual(d['FOO'].get(), 'foo')

    def test_set_list(self):
        d = MetaData()
        d['FOO'] = [1,2]
        self.assertIsInstance(d['FOO'], MetaList)
        self.assertEqual(d['FOO'].get(), [1,2])

    def test_set_list_2(self):
        d = MetaData()
        d['FOO'] = [1,2]
        d['FOO'] = [3,4]
        self.assertIsInstance(d['FOO'], MetaList)
        self.assertEqual(d['FOO'].get(), [3,4])

    def test_set_dict(self):
        d = MetaData()
        d['FOO'] = { 'foo': 42 }
        self.assertIsInstance(d['FOO'], MetaDict)
        self.assertEqual(d['FOO'].get(), { 'foo': 42 })

    def test_set_int(self):
        d = MetaData()
        d['FOO'] = 42
        self.assertIsInstance(d['FOO'], MetaInt)
        self.assertEqual(d['FOO'].get(), 42)

    def test_set_true(self):
        d = MetaData()
        d['FOO'] = True
        self.assertIsInstance(d['FOO'], MetaBool)
        self.assertEqual(d['FOO'].get(), True)

    def test_set_false(self):
        d = MetaData()
        d['FOO'] = False
        self.assertIsInstance(d['FOO'], MetaBool)
        self.assertEqual(d['FOO'].get(), False)

    def test_set_metastring_1(self):
        d = MetaData()
        d['FOO'] = MetaString(d, value='foo')
        self.assertIsInstance(d['FOO'], MetaString)
        self.assertEqual(d['FOO'].get(), 'foo')

    def test_set_invalid_type(self):
        d = MetaData()
        class Foo(object):
            pass
        with self.assertRaises(TypeError):
            d['FOO'] = Foo()

    def test_signature_1(self):
        d = MetaData()
        d['integer'] = 42
        d['string'] = 'Hello world'
        d['list'] = [ 4, 2 ]
        d['map'] = { 'foo': 1, 'bar': 2 }
        sig1 = d.signature()
        del d['list']
        sig2 = d.signature()
        d['list'] = [ 4, 2 ]
        sig3 = d.signature()
        self.assertEqual(sig1, sig3)
        self.assertNotEqual(sig1, sig2)

    def test_signature_2(self):
        d = MetaData()
        d['i'] = 42
        d['s'] = 'Hello world'
        d['list'] = [ 4, 2 ]
        d['map'] = { 'foo': 1, 'bar': 2 }
        sig1 = d.signature(t=dict)
        del d['s']
        sig2 = d.signature(t=dict)
        d['s'] = 'Hello world'
        sig3 = d.signature(t=dict)
        self.assertEqual(sig1, sig3)
        self.assertNotEqual(sig1, sig2)

    def test_signature_3(self):
        d1 = MetaData()
        d1['i'] = 42
        d1['s'] = 'Hello world'
        d1['list'] = [ 4, 2 ]
        d1['map'] = { 'foo': 1, 'bar': 2 }
        d2 = MetaData()
        d2['i'] = 42
        d2['s'] = 'Hello world'
        d2['list'] = [ 4, 2 ]
        d2['map'] = { 'foo': 1, 'bar': 2 }
        self.assertEqual(d1.signature(), d2.signature())
        d2['foo'] = 'bar'
        self.assertNotEqual(d1.signature(), d2.signature())

    def test_signature_4(self):
        d = MetaData()
        d['i'] = 42
        d['s'] = 'Hello world'
        d['list'] = [ 4, 2 ]
        d['map'] = { 'foo': 1, 'bar': 2 }
        sig1 = d.signature()
        del d['s']
        sig2 = str(d.signature())
        d['s'] = 'Hello world'
        sig3 = str(d.signature())
        self.assertEqual(sig1, sig3)
        self.assertNotEqual(sig1, sig2)

    def test_signature_5(self):
        d = MetaData()
        d['i'] = 42
        with self.assertRaises(TypeError):
            d.signature(t=int)

    def test_signature_6(self):
        d = MetaData()
        d['i'] = 42
        with self.assertRaises(TypeError):
            d.signature(t=list)

    def test_signature_7(self):
        d = MetaData()
        d['i'] = 42
        with self.assertRaises(TypeError):
            d.signature(t=42)

    def test_signature_8(self):
        src = MetaData()
        MetaVar(src, 'FOO', 'foo')
        self.assertFalse(src == 42)

    def test_flattened_1(self):
        d = MetaData()
        d['FOO'] = 'foo'
        f = d.flattened()
        self.assertEqual(f, {'FOO': 'foo'})

    def test_flattened_2a(self):
        d = MetaData()
        d['D'] = {}
        d['D']['foo'] = [1,2,3]
        d['D']['bar'] = "Hello world!"
        d['D']['foobar'] = {'foo': 1, 'bar': 2}
        d['i'] = 42
        f = d.flattened()
        self.assertEqual(f, {'D': {'foo': [1,2,3], 'bar': 'Hello world!',
                                   'foobar': {'foo': 1, 'bar': 2}},
                             'i': 42})

    def test_flattened_2b(self):
        d = MetaData()
        d['D'] = {}
        d['D']['foo'] = [1,2,3]
        d['D']['bar'] = "Hello world!"
        d['D']['foobar'] = {'foo': 1, 'bar': 2}
        d['D'].expand = 'clean'
        d['i'] = 42
        f = d.flattened()
        self.assertEqual(f, {'D': {'foo': [1,2,3], 'bar': 'Hello world!',
                                   'foobar': {'foo': 1, 'bar': 2}},
                             'i': 42})

    def test_flattened_2c(self):
        d = MetaData()
        d['D'] = {}
        d['D']['foo'] = [1,2,3]
        d['D']['bar'] = "Hello world!"
        d['D']['foobar'] = {'foo': 1, 'bar': 2}
        d['D'].expand = 'partial'
        d['i'] = 42
        f = d.flattened()
        self.assertEqual(f, {'D': {'foo': [1,2,3], 'bar': 'Hello world!',
                                   'foobar': {'foo': 1, 'bar': 2}},
                             'i': 42})


class TestMetaVar(unittest.TestCase):

    def setUp(self):
        pass

    def test_init_default(self):
        d = MetaData()
        VAR = MetaVar(d)
        self.assertIsInstance(VAR, MetaString)

    def test_init_string(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        self.assertIsInstance(VAR, MetaString)

    def test_init_metastring(self):
        d = MetaData()
        VAR = MetaVar(d, value=MetaVar(d, value='foo'))
        self.assertIsInstance(VAR, MetaString)

    def test_init_list(self):
        d = MetaData()
        VAR = MetaVar(d, value=[42])
        self.assertIsInstance(VAR, MetaList)

    def test_init_metalist(self):
        d = MetaData()
        VAR = MetaVar(d, value=MetaVar(d, value=[42]))
        self.assertIsInstance(VAR, MetaList)

    def test_del(self):
        d = MetaData()
        MetaVar(d, 'VAR', 'foobar')
        self.assertEqual(d['VAR'].get(), 'foobar')
        del d['VAR']
        with self.assertRaises(KeyError):
            d['VAR']

    def test_cache_set(self):
        d = MetaData()
        MetaVar(d, 'VAR', 'foo')
        self.assertEqual(d['VAR'].get(), 'foo')
        d['VAR'].set('bar')
        self.assertEqual(d['VAR'].get(), 'bar')

    def test_cache_append(self):
        d = MetaData()
        MetaVar(d, 'VAR', 'foo')
        self.assertEqual(d['VAR'].get(), 'foo')
        d['VAR'].append('bar')
        self.assertEqual(d['VAR'].get(), 'foobar')

    def test_cache_prepend(self):
        d = MetaData()
        MetaVar(d, 'VAR', 'foo')
        self.assertEqual(d['VAR'].get(), 'foo')
        d['VAR'].prepend('bar')
        self.assertEqual(d['VAR'].get(), 'barfoo')

    def test_cache_override_if(self):
        d = MetaData()
        MetaVar(d, 'VAR', 'foo')
        self.assertEqual(d['VAR'].get(), 'foo')
        d['OVERRIDES'].append('USE_bar')
        d['VAR'].override_if['USE_bar'] = 'bar'
        self.assertEqual(d['VAR'].get(), 'bar')

    def test_cache_append_if(self):
        d = MetaData()
        MetaVar(d, 'VAR', 'foo')
        self.assertEqual(d['VAR'].get(), 'foo')
        d['OVERRIDES'].append('USE_bar')
        d['VAR'].append_if['USE_bar'] = 'bar'
        self.assertEqual(d['VAR'].get(), 'foobar')

    def test_cache_prepend_if(self):
        d = MetaData()
        MetaVar(d, 'VAR', 'foo')
        self.assertEqual(d['VAR'].get(), 'foo')
        d['OVERRIDES'].append('USE_bar')
        d['VAR'].prepend_if['USE_bar'] = 'bar'
        self.assertEqual(d['VAR'].get(), 'barfoo')

    def test_cache_strexpand_depends(self):
        d = MetaData()
        d['FOO'] = 'foo'
        d['BAR'] = MetaString(d, value="${FOO}bar")
        self.assertEqual(d['BAR'].get(), 'foobar')
        d['FOO'] = 'fuu'
        self.assertEqual(d['BAR'].get(), 'fuubar')

    def test_cache_python_depends(self):
        d = MetaData()
        d['FOO'] = 'foo'
        d['BAR'] = MetaString(d, value=PythonExpression("FOO + 'bar'"))
        self.assertEqual(d['BAR'].get(), 'foobar')
        d['FOO'] = 'fuu'
        self.assertEqual(d['BAR'].get(), 'fuubar')

    def test_signature_1(self):
        d1 = MetaData()
        d1['foobar'] = 'Hello world'
        d2 = MetaData()
        d2['foobar'] = 'Hello world'
        sig1 = d1['foobar'].signature()
        sig2 = str(d2['foobar'].signature())
        self.assertEqual(sig1, sig2)

    def test_signature_2(self):
        d = MetaData()
        d['x'] = 'Hello world'
        sig = d['x'].signature()
        self.assertFalse(sig == 42)

    def test_signature_3(self):
        d = MetaData()
        d['x'] = 'Hello world'
        sig = d['x'].signature()
        self.assertTrue(sig != 42)

    def test_print_1(self):
        d = MetaData()
        import io
        output = io.StringIO()
        d['FOO'] = ['foo']
        d['FOO'].append("bar")
        del d['OVERRIDES']
        d.print(file=output)
        self.assertEqual(output.getvalue(), "FOO = ['foo', 'bar']\n")

    def test_print_2(self):
        d = MetaData()
        import io
        output = io.StringIO()
        d['FOO'] = {'foo': 1}
        del d['OVERRIDES']
        d.print(file=output)
        self.assertEqual(output.getvalue(), "FOO = {'foo': 1}\n")

    def test_is_solitary_1(self):
        d = MetaData()
        d['FOO'] = 'foo'
        self.assertTrue(d.is_solitary('FOO'))

    def test_is_solitary_2a(self):
        d = MetaData()
        d['FOO'] = 'foo'
        d['BAR'] = ''
        d['BAR'].set(PythonExpression("FOO + 'bar'"))
        self.assertFalse(d.is_solitary('FOO'))

    def test_is_solitary_2b(self):
        d = MetaData()
        d['FOO'] = 'foo'
        d['BAR'] = ''
        d['BAR'].set("${FOO}bar")
        self.assertFalse(d.is_solitary('FOO'))

    def test_is_solitary_3(self):
        d = MetaData()
        d['FOO'] = 'foo'
        d['BAR'] = ''
        d['BAR'].set("bar")
        self.assertTrue(d.is_solitary(d['FOO']))
        self.assertTrue(d.is_solitary(d['BAR']))

    def test_is_solitary_4a(self):
        d = MetaData()
        d['FOO'] = 'foo'
        d['BAR'] = 'bar'
        self.assertTrue(d.is_solitary(d['FOO']))

    def test_is_solitary_4b(self):
        d = MetaData()
        d['FOO'] = 'foo'
        d['BAR'] = 'bar'
        self.assertTrue(d.is_solitary('FOO'))

    def test_is_solitary_5(self):
        d = MetaData()
        d['FOO'] = 'foo'
        d['BAR'] = 'bar'
        d['BAR'].override_if['foo'] = '${FOO}'
        self.assertTrue(d.is_solitary('FOO'))
        d['OVERRIDES'].append('foo')
        self.assertFalse(d.is_solitary('FOO'))


class TestMetaInt(unittest.TestCase):

    def setUp(self):
        pass

    def test_var_expand_1(self):
        d = MetaData()
        MetaVar(d, 'FOO', 42)
        self.assertEqual(d['FOO'].get(), 42)



class TestMetaString(unittest.TestCase):

    def setUp(self):
        pass

    def test_set_get_str(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        VAR.set('bar')
        self.assertEqual(VAR.get(), 'bar')

    def test_set_get_metastring(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        VAR.set(MetaVar(d, value='bar'))
        self.assertEqual(VAR.get(), 'bar')

    def test_set_list(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        self.assertRaises(TypeError, VAR.set, (['bar']))

    def test_set_dict(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        self.assertRaises(TypeError, VAR.set, ({'foo': 42}))

    def test_set_bool(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        self.assertRaises(TypeError, VAR.set, (False))

    def test_set_int(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        self.assertRaises(TypeError, VAR.set, (42))

    def test_set_code_str_1(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        VAR.set(PythonExpression('"bar"'))
        self.assertEqual(VAR.get(), 'bar')

    def test_set_code_str_2(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        VAR.set(PythonExpression('"bar"', lineno=42))
        self.assertEqual(VAR.get(), 'bar')

    def test_set_code_list(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        VAR.set(PythonExpression('[1,2]'))
        self.assertRaises(TypeError, VAR.get)

    def test_set_code_dict(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        VAR.set(PythonExpression("{'bar': 42}"))
        self.assertRaises(TypeError, VAR.get)

    def test_set_code_bool(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        VAR.set(PythonExpression("'foo'=='bar'"))
        self.assertRaises(TypeError, VAR.get)

    def test_set_code_int(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        VAR.set(PythonExpression('6*7'))
        self.assertRaises(TypeError, VAR.get)

    def test_prepend_1(self):
        d = MetaData()
        VAR = MetaVar(d, value='bar')
        VAR.prepend('foo')
        self.assertEqual(VAR.get(), 'foobar')

    def test_prepend_2(self):
        d = MetaData()
        VAR = MetaVar(d, value='bar')
        VAR.prepend('foo')
        VAR.prepend('x')
        self.assertEqual(VAR.get(), 'xfoobar')

    def test_prepend_none(self):
        d = MetaData()
        VAR = MetaVar(d, value='bar')
        VAR.prepend('foo')
        VAR.prepend(None)
        self.assertEqual(VAR.get(), 'foobar')

    def test_prepend_metastring(self):
        d = MetaData()
        VAR = MetaVar(d, value='bar')
        VAR.prepend(MetaVar(d, value='foo'))
        VAR.prepend(MetaVar(d, value='x'))
        self.assertEqual(VAR.get(), 'xfoobar')

    def test_prepend_list(self):
        d = MetaData()
        VAR = MetaVar(d, value='bar')
        with self.assertRaises(TypeError):
            VAR.prepend(MetaVar(d, value=[42]))

    def test_prepend_code_list(self):
        d = MetaData()
        VAR = MetaVar(d, value='bar')
        VAR.prepend(value=PythonExpression('[42]'))
        with self.assertRaises(TypeError):
            VAR.get()

    def test_prepend_to_none_1(self):
        d = MetaData()
        VAR = MetaVar(d, value='bar')
        VAR.set(None)
        VAR.prepend('foo')
        self.assertEqual(VAR.get(), 'foo')

    def test_prepend_to_none_2(self):
        d = MetaData()
        VAR = MetaVar(d, value='bar')
        VAR.set(None)
        VAR.prepend('foo')
        self.assertEqual(VAR.get(evaluate=False), "'foo'")

    def test_override_with_none_1(self):
        d = MetaData()
        VAR = MetaVar(d, value='bar')
        VAR.override_if['foo'] = None
        d['OVERRIDES'].append('foo')
        self.assertEqual(VAR.get(evaluate=False), None)

    def test_append_1(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        VAR.append('bar')
        self.assertEqual(VAR.get(), 'foobar')

    def test_append_2(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        VAR.append('bar')
        VAR.append('x')
        self.assertEqual(VAR.get(), 'foobarx')

    def test_append_none(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        VAR.append('bar')
        VAR.append(None)
        self.assertEqual(VAR.get(), 'foobar')

    def test_append_metastring(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        VAR.append(MetaVar(d, value='bar'))
        VAR.append(MetaVar(d, value='x'))
        self.assertEqual(VAR.get(), 'foobarx')

    def test_append_list(self):
        d = MetaData()
        VAR = MetaVar(d, value='bar')
        with self.assertRaises(TypeError):
            VAR.append(MetaVar(d, value=[42]))

    def test_append_code_list(self):
        d = MetaData()
        VAR = MetaVar(d, value='bar')
        VAR.append(value=PythonExpression('[42]'))
        with self.assertRaises(TypeError):
            VAR.get()

    def test_append_to_none_1(self):
        d = MetaData()
        VAR = MetaVar(d, value='bar')
        VAR.set(None)
        VAR.append('foo')
        self.assertEqual(VAR.get(), 'foo')

    def test_append_to_none_2(self):
        d = MetaData()
        VAR = MetaVar(d, value='bar')
        VAR.set(None)
        VAR.append('foo')
        self.assertEqual(VAR.get(evaluate=False), "'foo'")

    def test_add_str(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        VAR += 'bar'
        self.assertEqual(VAR.get(), 'foobar')

    def test_add_metastring(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        VAR += MetaVar(d, value='bar')
        self.assertEqual(VAR.get(), 'foobar')

    def test_add_self(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        VAR += VAR
        self.assertEqual(VAR.get(), 'foofoo')

    def test_add_list(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        with self.assertRaises(TypeError):
            VAR += [42]

    def test_add_dict(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        with self.assertRaises(TypeError):
            VAR += {'bar': 42}

    def test_add_int(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        with self.assertRaises(TypeError):
            VAR += 42

    def test_add_true(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        with self.assertRaises(TypeError):
            VAR += True

    def test_add_false(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        with self.assertRaises(TypeError):
            VAR += False

    def test_add_2(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        ADDED = VAR + VAR
        self.assertEqual(ADDED.get(), 'foofoo')
        self.assertEqual(VAR.get(), 'foo')

    def test_add_3(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        ADDED = VAR + VAR + VAR
        self.assertEqual(ADDED.get(), 'foofoofoo')
        self.assertEqual(VAR.get(), 'foo')

    def test_add_3_mixed(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        ADDED = VAR + 'bar' + VAR
        self.assertEqual(ADDED.get(), 'foobarfoo')
        self.assertEqual(VAR.get(), 'foo')

    def test_add_4(self):
        d = MetaData()
        d['FOO'] = 'foo'
        d['FOO'].override_if['x'] = 'xxx'
        self.assertEqual(d['FOO'].get(), 'foo')
        d['OVERRIDES'] = ['x']
        self.assertEqual(d['FOO'].get(), 'xxx')
        d['FOO'] += 'bar'
        d['OVERRIDES'] = []
        self.assertEqual(d['FOO'].get(), 'foobar')
        d['OVERRIDES'] = ['x']
        self.assertEqual(d['FOO'].get(), 'xxx')

    def test_set_invalid_attr(self):
        d = MetaData()
        VAR = MetaVar(d, value='')
        with self.assertRaises(AttributeError):
            VAR.foo = 'bar'

    def test_set_code(self):
        d = MetaData()
        VAR = MetaVar(d)
        VAR.set(PythonExpression('"foo" + "bar"'))
        self.assertEqual(VAR.get(), 'foobar')

    def test_prepend_code(self):
        d = MetaData()
        VAR = MetaVar(d, value='bar')
        VAR.prepend(PythonExpression('"foo"'))
        self.assertEqual(VAR.get(), 'foobar')

    def test_append_code(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        VAR.append(PythonExpression('"bar"'))
        self.assertEqual(VAR.get(), 'foobar')

    def test_set_code_with_metavars(self):
        d = MetaData()
        MetaVar(d, 'FOO', 'foo')
        MetaVar(d, 'BAR', 'bar')
        VAR = MetaVar(d)
        VAR.set(PythonExpression('FOO + " " + BAR'))
        value = VAR.get()
        self.assertEqual(value, 'foo bar')

    def test_iter(self):
        d = MetaData()
        VAR = MetaVar(d, value='foobar')
        value = ''
        for c in VAR:
            value += c
        self.assertEqual(value, 'foobar')

    def test_override_1(self):
        d = MetaData()
        VAR = MetaVar(d, value='bar')
        VAR.override_if['USE_foo'] = 'foo'
        d['OVERRIDES'] = ['USE_foo']
        self.assertEqual(VAR.get(), 'foo')

    def test_override_2(self):
        d = MetaData()
        VAR = MetaVar(d, value='')
        d['OVERRIDES'] = ['USE_foo', 'USE_bar']
        VAR.override_if['USE_foo'] = 'foo'
        VAR.override_if['USE_bar'] = 'bar'
        self.assertEqual(VAR.get(), 'foo')

    def test_override_3(self):
        d = MetaData()
        VAR = MetaVar(d, value='bar')
        VAR.override_if['USE_foo'] = PythonExpression('[42]')
        d['OVERRIDES'] = ['USE_foo']
        self.assertRaises(TypeError, VAR.get)

    def test_prepend_if_1(self):
        d = MetaData()
        VAR = MetaVar(d, value='bar')
        d['OVERRIDES'] = ['USE_foo']
        VAR.prepend_if['USE_foo'] = 'foo'
        self.assertEqual(VAR.get(), 'foobar')

    def test_prepend_if_2(self):
        d = MetaData()
        VAR = MetaVar(d, value='x')
        d['OVERRIDES'] = ['USE_bar', 'USE_foo']
        VAR.prepend_if['USE_foo'] = 'foo'
        VAR.prepend_if['USE_bar'] = 'bar'
        self.assertEqual(VAR.get(), 'foobarx')

    def test_prepend_if_metastring_1(self):
        d = MetaData()
        VAR = MetaVar(d, value='x')
        d['OVERRIDES'] = ['USE_foo', 'USE_bar']
        VAR.prepend_if['USE_foo'] = MetaVar(d, value='foo')
        self.assertEqual(VAR.get(), 'foox')

    def test_prepend_if_metastring_2(self):
        d = MetaData()
        VAR = MetaVar(d, value='x')
        d['OVERRIDES'] = ['USE_foo', 'USE_bar']
        a = MetaVar(d, value='foo')
        a += 'bar'
        VAR.prepend_if['USE_foo'] = a
        self.assertEqual(VAR.get(), 'foobarx')

    def test_prepend_if_metastring_3(self):
        d = MetaData()
        VAR = MetaVar(d, value='x')
        d['OVERRIDES'] = ['USE_foo', 'USE_bar']
        VAR.prepend_if['USE_foo'] = MetaVar(d, value='foo')
        VAR.prepend_if['USE_bar'] = MetaVar(d, value='bar')
        self.assertEqual(VAR.get(), 'barfoox')

    def test_prepend_if_code_list(self):
        d = MetaData()
        VAR = MetaVar(d, value='x')
        d['OVERRIDES'] = ['USE_foo']
        VAR.prepend_if['USE_foo'] = PythonExpression('[42]')
        self.assertRaises(TypeError, VAR.get)

    def test_prepend_if_to_none(self):
        d = MetaData()
        VAR = MetaVar(d, value='x')
        VAR.set(None)
        d['OVERRIDES'] = ['USE_foo']
        VAR.prepend_if['USE_foo'] = 'foo'
        self.assertEqual(VAR.get(), 'foo')

    def test_append_if_1(self):
        d = MetaData()
        VAR = MetaVar(d, value='foo')
        d['OVERRIDES'] = ['USE_bar']
        VAR.append_if['USE_bar'] = 'bar'
        self.assertEqual(VAR.get(), 'foobar')

    def test_append_if_2(self):
        d = MetaData()
        VAR = MetaVar(d, value='x')
        d['OVERRIDES'] = ['USE_foo', 'USE_bar']
        VAR.append_if['USE_foo'] = 'foo'
        VAR.append_if['USE_bar'] = 'bar'
        self.assertEqual(VAR.get(), 'xfoobar')

    def test_append_if_metastring_1(self):
        d = MetaData()
        VAR = MetaVar(d, value='x')
        d['OVERRIDES'] = ['USE_foo', 'USE_bar']
        VAR.append_if['USE_foo'] = MetaVar(d, value='foo')
        self.assertEqual(VAR.get(), 'xfoo')

    def test_append_if_metastring_2(self):
        d = MetaData()
        VAR = MetaVar(d, value='x')
        d['OVERRIDES'] = ['USE_foo', 'USE_bar']
        a = MetaVar(d, value='foo')
        a += 'bar'
        VAR.append_if['USE_foo'] = a
        self.assertEqual(VAR.get(), 'xfoobar')

    def test_append_if_metastring_3(self):
        d = MetaData()
        VAR = MetaVar(d, value='x')
        d['OVERRIDES'] = ['USE_foo', 'USE_bar']
        VAR.append_if['USE_foo'] = MetaVar(d, value='foo')
        VAR.append_if['USE_bar'] = MetaVar(d, value='bar')
        self.assertEqual(VAR.get(), 'xfoobar')

    def test_append_if_code_list(self):
        d = MetaData()
        VAR = MetaVar(d, value='x')
        d['OVERRIDES'] = ['USE_foo']
        VAR.append_if['USE_foo'] = PythonExpression('[42]')
        self.assertRaises(TypeError, VAR.get)

    def test_append_if_to_none(self):
        d = MetaData()
        VAR = MetaVar(d, value='x')
        VAR.set(None)
        d['OVERRIDES'] = ['USE_foo']
        VAR.append_if['USE_foo'] = 'foo'
        self.assertEqual(VAR.get(), 'foo')

    def test_str(self):
        d = MetaData()
        VAR = MetaVar(d, value='foobar')
        self.assertEqual(str(VAR), 'foobar')

    def test_get_invalid_type(self):
        d = MetaData()
        VAR = MetaVar(d, value='')
        VAR.set(PythonExpression('["foo"]'))
        self.assertRaises(TypeError, VAR.get)

    def test_len(self):
        d = MetaData()
        VAR = MetaVar(d, value='foobar')
        self.assertEqual(len(VAR), 6)

    def test_contains(self):
        d = MetaData()
        VAR = MetaVar(d, value='foobar')
        self.assertTrue('f' in VAR)
        self.assertFalse('z' in VAR)

    def test_index(self):
        d = MetaData()
        VAR = MetaVar(d, value='foobar')
        self.assertEqual(VAR.index('b'), 3)

    def test_count(self):
        d = MetaData()
        VAR = MetaVar(d, value='foobar')
        self.assertEqual(VAR.count('o'), 2)
        self.assertEqual(VAR.count('r'), 1)

    def test_eval_stack_1(self):
        d = MetaData()
        MetaVar(d, 'FOO', 'foo')
        MetaVar(d, 'BAR', 'bar')
        MetaVar(d, 'FOOBAR', PythonExpression('FOO + BAR'))
        self.assertEqual(d['FOOBAR'].get(), 'foobar')

    def test_eval_stack_recursive(self):
        d = MetaData()
        FOO = MetaVar(d, 'FOO', PythonExpression('BAR'))
        BAR = MetaVar(d, 'BAR', PythonExpression('FOO'))
        self.assertRaises(MetaDataRecursiveEval, FOO.get)

    def test_var_expand_default_method(self):
        d = MetaData()
        MetaVar(d, 'FOO', 'foo')
        self.assertEqual(d['FOO'].expand, 'full')

    def test_var_expand_1(self):
        d = MetaData()
        MetaVar(d, 'FOO', 'foo')
        MetaVar(d, 'BAR', 'bar')
        MetaVar(d, 'FOOBAR', '${FOO}${BAR}')
        self.assertEqual(d['FOOBAR'].get(), 'foobar')

    def test_var_expand_2(self):
        d = MetaData()
        MetaVar(d, 'X', 'x')
        MetaVar(d, 'Y', '${X}y')
        MetaVar(d, 'Z', '${Y}z')
        self.assertEqual(d['Z'].get(), 'xyz')

    def test_var_expand_3(self):
        d = MetaData()
        MetaVar(d, 'FOO', 'foo')
        MetaVar(d, 'BAR', 'bar')
        MetaVar(d, 'FOOBAR', '${FOO}${BAR}')
        self.assertEqual(d['FOOBAR'].get(), 'foobar')
        d['FOO'] = 'xfoox'
        self.assertEqual(d['FOOBAR'].get(), 'xfooxbar')

    def test_var_expand_full(self):
        d = MetaData()
        MetaVar(d, 'FOO', 'foo')
        FOOBAR = MetaVar(d, 'FOOBAR', '${FOO}${BAR}')
        FOOBAR.expand = 'full'
        self.assertRaises(KeyError, FOOBAR.get)

    def test_var_expand_partial(self):
        d = MetaData()
        MetaVar(d, 'FOO', 'foo')
        FOOBAR = MetaVar(d, 'FOOBAR', '${FOO}${BAR}')
        FOOBAR.expand = 'partial'
        self.assertEqual(d['FOOBAR'].get(), 'foo${BAR}')

    def test_var_expand_clean_1(self):
        d = MetaData()
        MetaVar(d, 'FOO', 'foo')
        FOOBAR = MetaVar(d, 'FOOBAR', '${FOO}${BAR}')
        FOOBAR.expand = 'clean'
        self.assertEqual(d['FOOBAR'].get(), 'foo')

    def test_var_expand_clean_2(self):
        d = MetaData()
        MetaVar(d, 'FOO', 'foo')
        FOOBAR = MetaVar(d, 'FOOBAR', '${FOO}${BAR}')
        FOOBAR.expand = 'clean'
        self.assertEqual(d['FOOBAR'].get(), 'foo')
        MetaVar(d, 'BAR', 'bar')
        self.assertEqual(d['FOOBAR'].get(), 'foobar')

    def test_var_expand_no(self):
        d = MetaData()
        MetaVar(d, 'FOO', 'foo')
        FOOBAR = MetaVar(d, 'FOOBAR', '${FOO}${BAR}')
        FOOBAR.expand = 'no'
        self.assertEqual(d['FOOBAR'].get(), '${FOO}${BAR}')

    def test_var_expand_invalid(self):
        d = MetaData()
        MetaVar(d, 'FOO', 'foo')
        FOOBAR = MetaVar(d, 'FOOBAR', '${FOO}${BAR}')
        FOOBAR.expand = 'hello world'
        self.assertRaises(TypeError, FOOBAR.get)

    def test_var_expand_override_change(self):
        d = MetaData()
        FOO = MetaVar(d, 'FOO', '')
        FOO.override_if['USE_foo'] = 'foo'
        self.assertEqual(d['FOO'].get(), '')
        d['OVERRIDES'] = ['USE_foo']
        self.assertEqual(FOO.get(), 'foo')

    def test_var_expand_override(self):
        d = MetaData()
        FOO = MetaVar(d, 'FOO', '')
        FOO.override_if['USE_foo'] = 'foo'
        MetaVar(d, 'BAR', 'bar')
        MetaVar(d, 'FOOBAR', '${FOO}${BAR}')
        self.assertEqual(d['FOO'].get(), '')
        self.assertEqual(d['FOOBAR'].get(), 'bar')
        d['OVERRIDES'] = ['USE_foo']
        self.assertEqual(d['FOO'].get(), 'foo')
        self.assertEqual(d['FOOBAR'].get(), 'foobar')

    def test_var_expand_recursive(self):
        d = MetaData()
        FOO = MetaVar(d, 'FOO', '${BAR}')
        BAR = MetaVar(d, 'BAR', '${FOO}')
        self.assertRaises(MetaDataRecursiveEval, FOO.get)

    def test_var_expand_full_list(self):
        d = MetaData()
        FOO = MetaVar(d, 'FOO', [42])
        BAR = MetaVar(d, 'BAR', '${FOO}')
        BAR.expand = 'full'
        self.assertRaises(TypeError, BAR.get)

    def test_var_expand_partial_list(self):
        d = MetaData()
        FOO = MetaVar(d, 'FOO', [42])
        BAR = MetaVar(d, 'BAR', '${FOO}')
        BAR.expand = 'partial'
        self.assertRaises(TypeError, BAR.get)

    def test_var_expand_clean_list(self):
        d = MetaData()
        FOO = MetaVar(d, 'FOO', [42])
        BAR = MetaVar(d, 'BAR', '${FOO}')
        BAR.expand = 'clean'
        self.assertRaises(TypeError, BAR.get)

    def test_weak_set_1(self):
        d = MetaData()
        FOO = MetaString(d, 'FOO')
        FOO.weak_set('foo')
        self.assertEqual(FOO.get(), 'foo')

    def test_weak_set_2(self):
        d = MetaData()
        FOO = MetaString(d, 'FOO', 'foo')
        FOO.weak_set('bar')
        self.assertEqual(FOO.get(), 'foo')

    def test_print_1(self):
        d = MetaData()
        import io
        output = io.StringIO()
        d['FOO'] = 'foo'
        d['FOO'] += "bar"
        del d['OVERRIDES']
        d.print(file=output)
        self.assertEqual(output.getvalue(), "FOO = 'foobar'\n")

    def test_print_2(self):
        d = MetaData()
        import io
        output = io.StringIO()
        d['FOO'] = 'foo'
        d['FOO'].append('bar')
        del d['OVERRIDES']
        d.print(details=True, file=output)
        self.assertEqual(output.getvalue(),
                         "# FOO = 'foo' + 'bar'\nFOO = 'foobar'\n")

    def test_print_3(self):
        d = MetaData()
        import io
        output = io.StringIO()
        d['FOO'] = 'foo'
        d['FOO'].append('bar')
        d['FOO'].prepend(PythonExpression('BAZ'))
        d['BAZ'] = 'bazzz'
        d['FOO'].override_if['something'] = PythonExpression('HELLO')
        d['HELLO'] = 'Hello world'
        d['HELLO'].append(PythonExpression('BAZ'))
        d['OVERRIDES'].append('something')
        d.print(details=True, file=output)
        lines = output.getvalue().split('\n')
        self.assertTrue("# FOO = HELLO" in lines)
        self.assertTrue("FOO = 'Hello worldbazzz'" in lines)


class TestMetaList(unittest.TestCase):

    def setUp(self):
        pass

    def test_set_get_list(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        VAR.set(['bar'])
        self.assertEqual(VAR.get(), ['bar'])

    def test_set_get_metalist(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        VAR.set(MetaVar(d, value=['bar']))
        self.assertEqual(VAR.get(), ['bar'])

    def test_set_get_str(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        VAR.set(' foo bar ')
        self.assertEqual(VAR.get(), ['foo', 'bar'])

    def test_set_get_ints(self):
        d = MetaData()
        d['D'] = [1,2,3]
        self.assertEqual(d['D'].get(), [1,2,3])

    def test_set_bool(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        self.assertRaises(TypeError, VAR.set, (False))

    def test_set_int(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        self.assertRaises(TypeError, VAR.set, (42))

    def test_set_dict(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        self.assertRaises(TypeError, VAR.set, ({'foo': 42}))

    def test_prepend_1(self):
        d = MetaData()
        VAR = MetaVar(d, value=['bar'])
        VAR.prepend(['foo'])
        self.assertEqual(VAR.get(), ['foo', 'bar'])

    def test_prepend_2(self):
        d = MetaData()
        VAR = MetaVar(d, value=['bar'])
        VAR.prepend(['foo'])
        VAR.prepend(['x'])
        self.assertEqual(VAR.get(), ['x', 'foo', 'bar'])

    def test_prepend_metalist(self):
        d = MetaData()
        VAR = MetaVar(d, value=['bar'])
        VAR.prepend(MetaVar(d, value=['foo']))
        VAR.prepend(MetaVar(d, value=['x']))
        self.assertEqual(VAR.get(), ['x', 'foo', 'bar'])

    def test_prepend_string(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        VAR.prepend('bar')
        self.assertEqual(VAR.get(), ['bar', 'foo'])

    def test_append_1(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        VAR.append(['bar'])
        self.assertEqual(VAR.get(), ['foo', 'bar'])

    def test_append_2(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        VAR.append(['bar'])
        VAR.append(['x'])
        self.assertEqual(VAR.get(), ['foo', 'bar', 'x'])

    def test_append_metalist(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        VAR.append(['bar', 'x', 'y'])
        self.assertEqual(VAR.get(), ['foo', 'bar', 'x', 'y'])

    def test_append_string_1(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        VAR.append('bar')
        self.assertEqual(VAR.get(), ['foo', 'bar'])

    def test_append_string_2(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        VAR.append('bar x')
        self.assertEqual(VAR.get(), ['foo', 'bar', 'x'])

    def test_append_string_space(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        VAR.append(' bar    x ')
        self.assertEqual(VAR.get(), ['foo', 'bar', 'x'])

    def test_append_string_tab(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        VAR.append('\tbar\tx\t')
        self.assertEqual(VAR.get(), ['foo', 'bar', 'x'])

    def test_append_string_newline(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        VAR.append('\nbar\nx\n')
        self.assertEqual(VAR.get(), ['foo', 'bar', 'x'])

    def test_add_list(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        VAR += ['bar', 'x']
        self.assertEqual(VAR.get(), ['foo', 'bar', 'x'])

    def test_add_metalist(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        VAR += MetaVar(d, value=['bar', 'x'])
        self.assertEqual(VAR.get(), ['foo', 'bar', 'x'])

    def test_add_str(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        VAR += 'bar'
        self.assertEqual(VAR.get(), ['foo', 'bar'])

    def test_add_metastr(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        VAR += MetaVar(d, value='bar')
        self.assertEqual(VAR.get(), ['foo', 'bar'])

    def test_add_int(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        with self.assertRaises(TypeError):
            VAR += 42

    def test_add_true(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        with self.assertRaises(TypeError):
            VAR += True

    def test_add_false(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        with self.assertRaises(TypeError):
            VAR += False

    def test_add_dict(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        with self.assertRaises(TypeError):
            VAR += { 'bar': 42 }

    def test_set_invalid_attr(self):
        d = MetaData()
        VAR = MetaVar(d, value=[])
        with self.assertRaises(AttributeError):
            VAR.foo = 'bar'

    def test_iter(self):
        d = MetaData()
        VAR = MetaVar(d, value=[1,2,3])
        sum = 0
        for i in VAR:
            sum += i
        self.assertEqual(sum, 6)

    def test_iter_reversed(self):
        d = MetaData()
        VAR = MetaVar(d, value=[1,2,3])
        value = None
        for i in reversed(VAR):
            if value is None:
                value = i
            else:
                value = value - i
        self.assertEqual(value, 0)

    def test_override_1(self):
        d = MetaData()
        VAR = MetaVar(d, value=['bar'])
        d['OVERRIDES'] = ['USE_foo']
        VAR.override_if['USE_foo'] = ['foo']
        self.assertEqual(VAR.get(), ['foo'])

    def test_override_2(self):
        d = MetaData()
        VAR = MetaVar(d, value=[])
        d['OVERRIDES'] = ['USE_foo', 'USE_bar']
        VAR.override_if['USE_foo'] = ['foo']
        VAR.override_if['USE_bar'] = ['bar']
        self.assertEqual(VAR.get(), ['foo'])

    def test_prepend_if_1(self):
        d = MetaData()
        VAR = MetaVar(d, value=['bar'])
        d['OVERRIDES'] = ['USE_foo']
        VAR.prepend_if['USE_foo'] = ['foo']
        self.assertEqual(VAR.get(), ['foo', 'bar'])

    def test_prepend_if_2(self):
        d = MetaData()
        VAR = MetaVar(d, value=['x'])
        d['OVERRIDES'] = ['USE_bar', 'USE_foo']
        VAR.prepend_if['USE_foo'] = ['foo']
        VAR.prepend_if['USE_bar'] = ['bar']
        self.assertEqual(VAR.get(), ['foo', 'bar', 'x'])

    def test_prepend_if_string(self):
        d = MetaData()
        VAR = MetaVar(d, value=['x'])
        d['OVERRIDES'] = ['USE_foo']
        VAR.prepend_if['USE_foo'] = " foo  \t \n\t bar\n"
        self.assertEqual(VAR.get(), ['foo', 'bar', 'x'])

    def test_append_if_1(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo'])
        d['OVERRIDES'] = ['USE_bar']
        VAR.append_if['USE_bar'] = ['bar']
        self.assertEqual(VAR.get(), ['foo', 'bar'])

    def test_append_if_2(self):
        d = MetaData()
        VAR = MetaVar(d, value=['x'])
        d['OVERRIDES'] = ['USE_foo', 'USE_bar']
        VAR.append_if['USE_foo'] = ['foo']
        VAR.append_if['USE_bar'] = ['bar']
        self.assertEqual(VAR.get(), ['x', 'foo', 'bar'])

    def test_append_if_metalist_1(self):
        d = MetaData()
        VAR = MetaVar(d, value=['x'])
        d['OVERRIDES'] = ['USE_foo', 'USE_bar']
        VAR.append_if['USE_foo'] = MetaVar(d, value=['foo'])
        self.assertEqual(VAR.get(), ['x', 'foo'])

    def test_append_if_metastring_2(self):
        d = MetaData()
        VAR = MetaVar(d, value=['x'])
        d['OVERRIDES'] = ['USE_foo', 'USE_bar']
        a = MetaVar(d, value=['foo'])
        a += ['bar']
        VAR.append_if['USE_foo'] = a
        self.assertEqual(VAR.get(), ['x', 'foo', 'bar'])

    def test_append_if_metastring_3(self):
        d = MetaData()
        VAR = MetaVar(d, value='x')
        d['OVERRIDES'] = ['USE_foo', 'USE_bar']
        VAR.append_if['USE_foo'] = MetaVar(d, value='foo')
        VAR.append_if['USE_bar'] = MetaVar(d, value='bar')
        self.assertEqual(VAR.get(), 'xfoobar')

    def test_append_if_string(self):
        d = MetaData()
        VAR = MetaVar(d, value=['x'])
        d['OVERRIDES'] = ['USE_foo']
        VAR.append_if['USE_foo'] = " foo  \t \n\t bar\n"
        self.assertEqual(VAR.get(), ['x', 'foo', 'bar'])

    def test_str(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo', 'bar'])
        self.assertEqual(str(VAR), "foo bar")

    def test_str_no_separator(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo', 'bar'])
        VAR.separator = None
        self.assertEqual(str(VAR), "['foo', 'bar']")

    def test_str_colon_separator(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo', 'bar'])
        VAR.separator = ':'
        self.assertEqual(str(VAR), "foo:bar")

    def test_len(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo', 'bar'])
        self.assertEqual(len(VAR), 2)

    def test_contains(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo', 'bar'])
        self.assertTrue('foo' in VAR)
        self.assertFalse('hello' in VAR)

    def test_contains_1(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo', 'bar', 'hello'])
        self.assertEqual(VAR.index('hello'), 2)

    def test_contains_2(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo', 'bar', 'hello'])
        self.assertRaises(ValueError, VAR.index, ('foo', 1))

    def test_contains_3(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo', 'bar', 'hello'])
        self.assertEqual(VAR.index('hello', end=3), 2)

    def test_contains_4(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo', 'bar', 'hello'])
        with self.assertRaises(ValueError):
            VAR.index('hello', end=1)

    def test_count(self):
        d = MetaData()
        VAR = MetaVar(d, value=['foo', 'bar', 'hello', 'foo', 'bar'])
        self.assertEqual(VAR.count('hello'), 1)
        self.assertEqual(VAR.count('foo'), 2)

    def test_string_expand(self):
        d = MetaData()
        VAR = MetaVar(d, value=[])
        MetaVar(d, 'FOO', 'f o o')
        MetaVar(d, 'BAR', 'b a r')
        MetaVar(d, 'FOOBAR', "${FOO} ${BAR}")
        VAR.append("${FOOBAR}")
        self.assertEqual(VAR.get(), ['f', 'o', 'o', 'b', 'a', 'r'])

    def test_weak_set_1(self):
        d = MetaData()
        FOO = MetaList(d, 'FOO', None)
        FOO.weak_set(['foo'])
        self.assertEqual(FOO.get(), ['foo'])

    def test_weak_set_2(self):
        d = MetaData()
        FOO = MetaList(d, 'FOO', ['foo'])
        FOO.weak_set(['bar'])
        self.assertEqual(FOO.get(), ['foo'])

    def test_signature_1(self):
        d = MetaData()
        FOO = MetaList(d, 'FOO', ['foo', 42, [1, 'bar']])
        sig1 = str(FOO.signature())
        FOO.set([7,8])
        sig2 = str(FOO.signature())
        FOO.set(['foo', 42, [1,'bar']])
        sig3 = str(FOO.signature())
        self.assertEqual(sig1, sig3)
        self.assertNotEqual(sig1, sig2)

    def test_signature_2(self):
        d = MetaData()
        FOO = MetaList(d, 'FOO')
        FOO.set(PythonExpression("['bar']"))
        FOO.prepend('x')
        FOO.append('y')
        FOO.override_if['foo'] = [ 1 ]
        FOO.override_if['bar'] = [ 42, 7 ]
        sig1 = str(FOO.signature())
        FOO.set([666])
        sig2 = str(FOO.signature())
        FOO.set(PythonExpression("['bar']"))
        FOO.prepend('x')
        FOO.append('y')
        sig3 = str(FOO.signature())
        self.assertEqual(sig1, sig3)
        self.assertNotEqual(sig1, sig2)

    def test_signature_tuple(self):
        d = MetaData()
        FOO = MetaList(d, 'FOO', [(1, 2)])
        self.assertRaises(TypeError, FOO.signature)

    def test_signature_object(self):
        d = MetaData()
        class FooBar(object):
            pass
        FOO = MetaList(d, 'FOO', [FooBar()])
        self.assertRaises(TypeError, FOO.signature)


class TestMetaDict(unittest.TestCase):

    def setUp(self):
        pass

    def test_init_empty_dict(self):
        d = MetaData()
        MetaVar(d, 'VAR', {})
        self.assertIsInstance(d['VAR'], MetaDict)

    def test_init_dict(self):
        d = MetaData()
        MetaVar(d, 'VAR', {'foo': 1, 'bar': 2})
        self.assertIsInstance(d['VAR'], MetaDict)

    def test_init_dict_get(self):
        d = MetaData()
        MetaVar(d, 'VAR', {'foo': 1, 'bar': 2})
        self.assertEqual(d['VAR'].get(), {'foo': 1, 'bar': 2})

    def test_init_dict_getitem(self):
        d = MetaData()
        MetaVar(d, 'VAR', {'foo': 1, 'bar': 2})
        self.assertIsInstance(d['VAR']['foo'], MetaInt)
        self.assertIsInstance(d['VAR']['bar'], MetaInt)
        self.assertEqual(d['VAR']['foo'].get(), 1)
        self.assertEqual(d['VAR']['bar'].get(), 2)

    def test_init_none(self):
        d = MetaData()
        MetaDict(d, 'VAR', None)
        self.assertIsInstance(d['VAR'], MetaDict)

    def test_init_none_set_get(self):
        d = MetaData()
        MetaDict(d, 'VAR', None)
        d['VAR']['foo'] = 42
        self.assertIsInstance(d['VAR']['foo'], MetaInt)
        self.assertEqual(d['VAR']['foo'].get(), 42)

    def test_assign_1(self):
        d = MetaData()
        d['VAR'] = { 'foo': 1, 'bar': 2 }
        self.assertIsInstance(d['VAR'], MetaDict)
        self.assertIsInstance(d['VAR']['foo'], MetaInt)
        self.assertIsInstance(d['VAR']['bar'], MetaInt)
        self.assertEqual(d['VAR'].get(), {'foo': 1, 'bar': 2})
        self.assertEqual(d['VAR']['foo'].get(), 1)
        self.assertEqual(d['VAR']['bar'].get(), 2)

    def test_get_1(self):
        d = MetaData()
        d['FOO'] = { 'foo': 1, 'bar': 2 }
        self.assertEqual(d['FOO'].get(), { 'foo': 1, 'bar': 2 })

    def test_get_invalid(self):
        d = MetaData()
        d['FOO'] = {}
        d['FOO'].set(PythonExpression('42'))
        with self.assertRaises(TypeError):
            d['FOO'].get()

    def test_get_2(self):
        d = MetaData()
        d['FOO'] = {'foo': 1}
        d['BAR'] = {}
        d['BAR'].set(None)
        d['BAR'].update_if['foo'] = PythonExpression('FOO')
        d['OVERRIDES'].append('foo')
        self.assertEqual(d['BAR'].get(), {'foo': 1})
        self.assertEqual(d['BAR'].get(evaluate=False), 'FOO')

    def test_get_3(self):
        d = MetaData()
        d['FOO'] = {'foo': 1}
        d['BAR'] = {}
        d['BAR'].update_if['foo'] = PythonExpression('FOO')
        d['OVERRIDES'].append('foo')
        self.assertEqual(d['BAR'].get(evaluate=False), "{} + FOO")

    def test_get_4(self):
        d = MetaData()
        d['FOO'] = {'foo': 1}
        d['FOO'].override_if['bar'] = {'bar': 2}
        d['OVERRIDES'].append('bar')
        self.assertEqual(d['FOO'].get(), {'bar': 2})

    def test_get_5(self):
        d = MetaData()
        d['FOO'] = {'foo': 1}
        d['FOO'].set(None)
        d['FOO'].override_if['bar'] = {'bar': 2}
        d['OVERRIDES'].append('bar')
        self.assertEqual(d['FOO'].get(), {'bar': 2})

    def test_get_6(self):
        d = MetaData()
        d['FOO'] = {'foo': 1}
        d['FOO'].override_if['bar'] = None
        d['OVERRIDES'].append('bar')
        self.assertEqual(d['FOO'].get(), None)

    def test_get_7(self):
        d = MetaData()
        d['FOO'] = {'foo': 1}
        d['FOO'].override_if['bar'] = None
        d['OVERRIDES'].append('bar')
        self.assertEqual(d['FOO'].get(evaluate=False), None)

    def test_get_8(self):
        d = MetaData()
        d['FOO'] = {'foo': 1}
        d['FOO'].override_if['bar'] = {'bar': 7}
        d['OVERRIDES'].append('bar')
        self.assertEqual(d['FOO'].get(evaluate=False), "{'bar': 7}")

    # FIXME: add test cases to verify that a value of None updated with {}
    # gives {}, and a value of None updated with None gives None.

    def test_getitem_1(self):
        d = MetaData()
        d['FOO'] = { 'foo': 1, 'bar': 2 }
        self.assertEqual(d['FOO']['foo'].get(), 1)
        self.assertEqual(d['FOO']['bar'].get(), 2)

    def test_set_1(self):
        d = MetaData()
        d['FOO'] = {}
        d['FOO']['foo'] = 1
        d['FOO']['bar'] = 2
        self.assertEqual(d['FOO']['foo'].get(), 1)
        self.assertEqual(d['FOO']['bar'].get(), 2)

    def test_set_2(self):
        d = MetaData()
        d['FOO'] = {}
        d['FOO']['foo'] = 1
        d['FOO']['foo'] = 2
        self.assertEqual(d['FOO']['foo'].get(), 2)

    def test_set_3(self):
        d = MetaData()
        d['FOO'] = {}
        d['I'] = 2
        d['FOO']['foo'] = d['I']
        self.assertEqual(d['FOO']['foo'].get(), 2)

    def test_set_4(self):
        d = MetaData()
        d['FOO'] = {}
        d['FOO']['foo'] = 1
        d['I'] = 2
        d['FOO']['foo'] = d['I']
        self.assertEqual(d['FOO']['foo'].get(), 2)

    def test_weak_set_1(self):
        d = MetaData()
        VAR = MetaVar(d, value={'FOO': 'foo'})
        self.assertEqual(VAR.get()['FOO'], 'foo')
        VAR.set(None)
        self.assertIsNone(VAR.get())
        VAR.weak_set({'BAR': 'bar'})
        self.assertEqual(VAR.get()['BAR'], 'bar')
        VAR.weak_set({'HELLO': 'world'})
        with self.assertRaises(KeyError):
            VAR.get()['HELLO']
        self.assertEqual(VAR.get()['BAR'], 'bar')

    def test_del_1(self):
        d = MetaData()
        d['FOO'] = { 'foo': 1, 'bar': 2 }
        self.assertEqual(d['FOO']['foo'].get(), 1)
        del d['FOO']['foo']
        with self.assertRaises(KeyError):
            d['FOO']['foo']

    def test_del_2(self):
        d = MetaData()
        VAR = MetaDict(d, value=None)
        with self.assertRaises(KeyError):
            del VAR['x']

    def test_contains_1(self):
        d = MetaData()
        VAR = MetaVar(d, value={'foo': 1})
        self.assertTrue('foo' in VAR)
        self.assertFalse('bar' in VAR)

    def test_contains_2(self):
        d = MetaData()
        VAR = MetaVar(d, value={'foo': 1})
        VAR.set(None)
        self.assertFalse('foo' in VAR)

    def test_len_1(self):
        d = MetaData()
        d['FOO'] = { 'foo': 11, 'bar': 22 }
        self.assertEqual(len(d['FOO']), 2)

    def test_len_2(self):
        d = MetaData()
        d['FOO'] = {}
        self.assertEqual(len(d['FOO']), 0)

    def test_items_1(self):
        d = MetaData()
        d['FOO'] = { 'foo': 1, 'bar': 2 }
        self.assertEqual(sorted(list(d['FOO'].items())),
                         sorted([('foo', 1), ('bar', 2)]))

    def test_items_2(self):
        d = MetaData()
        d['FOO'] = {}
        self.assertEqual(list(d['FOO'].items()), [])

    def test_keys_1(self):
        d = MetaData()
        d['FOO'] = { 'foo': 1, 'bar': 2 }
        self.assertEqual(sorted(list(d['FOO'].keys())),
                         sorted(['foo', 'bar']))

    def test_keys_2(self):
        d = MetaData()
        d['FOO'] = {}
        self.assertEqual(list(d['FOO'].keys()), [])

    def test_iter(self):
        d = MetaData()
        VAR = MetaVar(d, value={'foo': 'x', 'bar': 'y'})
        l = set()
        for key in VAR:
            l.add(VAR.get()[key])
        self.assertTrue('x' in l)
        self.assertTrue('y' in l)
        self.assertFalse('z' in l)

    def test_struct_1(self):
        d = MetaData()
        d['FOO'] = {}
        d['FOO']['x'] = {}
        d['FOO']['x']['y'] = 42
        self.assertIsInstance(d['FOO'], MetaDict)
        self.assertIsInstance(d['FOO']['x'], MetaDict)
        self.assertIsInstance(d['FOO']['x']['y'], MetaInt)

    def test_struct_2(self):
        d = MetaData()
        d['FOO'] = {}
        d['FOO']['x'] = {}
        d['FOO']['x']['y'] = {}
        d['FOO']['x']['y']['z'] = 42
        self.assertIsInstance(d['FOO'], MetaDict)
        self.assertIsInstance(d['FOO']['x'], MetaDict)
        self.assertIsInstance(d['FOO']['x']['y'], MetaDict)
        self.assertIsInstance(d['FOO']['x']['y']['z'], MetaInt)
        self.assertEqual(d['FOO']['x']['y']['z'].get(), 42)
        self.assertEqual(d['FOO']['x']['y'].get()['z'], 42)
        self.assertEqual(d['FOO']['x'].get()['y']['z'], 42)
        self.assertEqual(d['FOO'].get()['x']['y']['z'], 42)
        self.assertEqual(d['FOO']['x']['y'].get()['z'], 42)

    def test_update_1(self):
        d = MetaData()
        d['VAR'] = {}
        d['VAR']['BAR'] = 'bar'
        d['VAR'].update(FOO='foo')
        self.assertEqual(d['VAR'].get()['BAR'], 'bar')
        self.assertEqual(d['VAR'].get()['FOO'], 'foo')

    def test_update_2(self):
        d = MetaData()
        d['VAR'] = {}
        d['VAR']['BAR'] = 'bar'
        d['VAR'].update({'FOO': 'foo'})
        self.assertEqual(d['VAR'].get()['BAR'], 'bar')
        self.assertEqual(d['VAR'].get()['FOO'], 'foo')

    def test_update_3(self):
        d = MetaData()
        d['VAR'] = {}
        d['VAR']['BAR'] = 'bar'
        V = MetaVar(d, value={'FOO': 'foo'})
        d['VAR'].update(V)
        self.assertEqual(d['VAR'].get()['BAR'], 'bar')
        self.assertEqual(d['VAR'].get()['FOO'], 'foo')

    def test_update_4(self):
        d = MetaData()
        d['VAR'] = {}
        d['VAR']['BAR'] = 'bar'
        MetaVar(d, 'V', {'FOO': 'foo'})
        d['VAR'].update(PythonExpression('V'))
        self.assertEqual(d['VAR'].get()['BAR'], 'bar')
        self.assertEqual(d['VAR'].get()['FOO'], 'foo')

    def test_update_invalid(self):
        d = MetaData()
        d['VAR'] = {}
        d['VAR']['BAR'] = 'bar'
        self.assertRaises(TypeError, d['VAR'].update, ([42]))

    def test_update_none(self):
        d = MetaData()
        d['VAR'] = {}
        d['VAR']['BAR'] = 'bar'
        d['VAR'].update(None)
        self.assertEqual(d['VAR'].get()['BAR'], 'bar')

    def test_override_if_1(self):
        d = MetaData()
        d['FOO'] = {}
        d['FOO']['foo'] = 42
        d['FOO'].override_if['USE_not_foo'] = {}
        self.assertEqual(d['FOO']['foo'].get(), 42)
        d['OVERRIDES'] = ['USE_not_foo']
        with self.assertRaises(KeyError):
            d['FOO'].get()['foo'].get()

    def test_override_if_2(self):
        d = MetaData()
        d['FOO'] = {}
        d['FOO']['BAR'] = {}
        d['FOO'].override_if['USE_foo'] = { 'foo': 42 }
        d['FOO']['BAR'].override_if['USE_bar'] = { 'bar': 43}
        with self.assertRaises(KeyError):
            d['FOO'].get()['foo']
        self.assertEqual(d['FOO'].get()['BAR'], {})
        with self.assertRaises(KeyError):
            d['FOO'].get()['BAR']['bar']
        d['OVERRIDES'] = ['USE_foo']
        self.assertEqual(d['FOO'].get()['foo'], 42)
        with self.assertRaises(KeyError):
            d['FOO'].get()['BAR']
        d['OVERRIDES'] = ['USE_bar']
        with self.assertRaises(KeyError):
            d['FOO'].get()['foo']
        self.assertEqual(d['FOO'].get()['BAR'], { 'bar': 43 })
        self.assertEqual(d['FOO'].get()['BAR']['bar'], 43)
        d['OVERRIDES'] = []
        with self.assertRaises(KeyError):
            d['FOO'].get()['foo']
        self.assertEqual(d['FOO'].get()['BAR'], {})
        with self.assertRaises(KeyError):
            d['FOO'].get()['BAR']['bar']

    def test_override_if_str(self):
        d = MetaData()
        d['FOO'] = {}
        with self.assertRaises(TypeError):
            d['FOO'].override_if['USE_foo'] = "foobar"

    def test_override_if_list(self):
        d = MetaData()
        d['FOO'] = {}
        d['FOO']['foo'] = 42
        with self.assertRaises(TypeError):
            d['FOO'].override_if['USE_foo'] = [42]

    def test_override_if_int(self):
        d = MetaData()
        d['FOO'] = {}
        d['FOO']['foo'] = 42
        with self.assertRaises(TypeError):
            d['FOO'].override_if['USE_foo'] = 42

    def test_override_if_invalid_code(self):
        d = MetaData()
        d['FOO'] = {}
        d['FOO']['foo'] = 42
        d['FOO'].override_if['USE_foo'] = PythonExpression('42')
        d['OVERRIDES'] = ['USE_foo']
        self.assertRaises(TypeError, d['FOO'].get)

    def test_update_if_none(self):
        d = MetaData()
        d['FOO'] = {}
        d['FOO']['BAR'] = {}
        d['FOO'].update_if['USE_foo'] = None
        self.assertEqual(d['FOO'].get()['BAR'], {})
        d['OVERRIDES'] = ['USE_foo']
        self.assertEqual(d['FOO'].get()['BAR'], {})

    def test_none_update_if_none(self):
        d = MetaData()
        d['FOO'] = {}
        d['FOO']['BAR'] = {}
        d['FOO']['BAR'].set(None)
        d['FOO']['BAR'].update_if['USE_foo'] = { 'foo': 42 }
        self.assertEqual(d['FOO'].get()['BAR'], None)
        d['OVERRIDES'] = ['USE_foo']
        self.assertEqual(d['FOO'].get()['BAR']['foo'], 42)

    def test_update_if_invalid(self):
        d = MetaData()
        d['FOO'] = {}
        d['FOO']['BAR'] = {}
        d['FOO'].update_if['USE_foo'] = PythonExpression('42')
        self.assertEqual(d['FOO'].get()['BAR'], {})
        d['OVERRIDES'] = ['USE_foo']
        with self.assertRaises(TypeError):
            d['FOO'].get()

    def test_override_and_update_if_1(self):
        d = MetaData()
        d['FOO'] = {}
        d['FOO']['foo'] = 42
        d['FOO'].override_if['USE_not_foo'] = {}
        d['FOO'].update_if['USE_bar'] = { 'bar': 43 }
        self.assertEqual(d['FOO']['foo'].get(), 42)
        with self.assertRaises(KeyError):
            d['FOO'].get()['bar']
        d['OVERRIDES'] = ['USE_not_foo']
        with self.assertRaises(KeyError):
            d['FOO'].get()['foo']
        with self.assertRaises(KeyError):
            d['FOO'].get()['bar']
        d['OVERRIDES'] = ['USE_bar']
        self.assertEqual(d['FOO'].get()['foo'], 42)
        self.assertEqual(d['FOO'].get()['bar'], 43)
        d['OVERRIDES'] = []
        self.assertEqual(d['FOO']['foo'].get(), 42)
        with self.assertRaises(KeyError):
            d['FOO'].get()['bar']

    def test_eval_1(self):
        d = MetaData()
        d['FILES'] = {}
        d['FILES']['${PN}'] = ['${base_bindir}', '${bindir}']
        d['FILES']['${PN}-doc'] = ['${docdir}']
        d['PN'] = 'foo'
        d['base_bindir'] = '/bin'
        d['docdir'] = '${datadir}/doc'
        d['datadir'] = '${prefix}/share'
        d['prefix'] = '/usr'
        d['bindir'] = '${prefix}/bin'
        self.assertEqual(d['FILES'].get(),
                         {'foo': ['/bin', '/usr/bin'],
                          'foo-doc': ['/usr/share/doc']})

    def test_eval_2(self):
        d = MetaData()
        d['FILES'] = {}
        d['FILES']['${PN}'] = ['${base_bindir}', '${bindir}']
        d['FILES']['${PN}-doc'] = ['${docdir}']
        d['FILES']['${PN}-doc'].override_if['USE_foo'] = []
        d['PN'] = 'foo'
        d['base_bindir'] = '/bin'
        d['docdir'] = '${datadir}/doc'
        d['datadir'] = '${prefix}/share'
        d['prefix'] = '/usr'
        d['bindir'] = '${prefix}/bin'
        self.assertEqual(d['FILES'].get(),
                         {'foo': ['/bin', '/usr/bin'],
                          'foo-doc': ['/usr/share/doc']})
        d['OVERRIDES'] = ['USE_foo']
        self.assertEqual(d['FILES'].get(),
                         {'foo': ['/bin', '/usr/bin'],
                          'foo-doc': []})

    def test_eval_3(self):
        d = MetaData()
        d['FILES'] = {}
        d['FILES']['${PN}'] = ['${base_bindir}', '${bindir}']
        d['FILES']['${PN}-doc'] = ['${docdir}']
        d['FILES']['${PN}-doc'].append_if['USE_foo'] = ['more']
        d['PN'] = 'foo'
        d['base_bindir'] = '/bin'
        d['docdir'] = '${datadir}/doc'
        d['datadir'] = '${prefix}/share'
        d['prefix'] = '/usr'
        d['bindir'] = '${prefix}/bin'
        self.assertEqual(d['FILES'].get(),
                         {'foo': ['/bin', '/usr/bin'],
                          'foo-doc': ['/usr/share/doc']})
        d['OVERRIDES'] = ['USE_foo']
        self.assertEqual(d['FILES'].get(),
                         {'foo': ['/bin', '/usr/bin'],
                          'foo-doc': ['/usr/share/doc', 'more']})

    def test_eval_4(self):
        d = MetaData()
        d['FILES'] = {}
        d['FILES']['${PN}'] = ['${base_bindir}', '${bindir}']
        d['FILES']['${PN}-doc'] = ['${docdir}']
        d['FILES']['${PN}-doc'].append_if['USE_foo'] = ['more']
        d['PN'] = 'foo'
        d['base_bindir'] = '/bin'
        d['docdir'] = '${datadir}/doc'
        d['datadir'] = '${prefix}/share'
        d['prefix'] = '/usr'
        d['bindir'] = '${prefix}/bin'
        d['FILES'].override_if['USE_foo'] = {}
        self.assertEqual(d['FILES'].get(),
                         {'foo': ['/bin', '/usr/bin'],
                          'foo-doc': ['/usr/share/doc']})
        d['OVERRIDES'] = ['USE_foo']
        self.assertEqual(d['FILES'].get(), {})

    def test_eval_5(self):
        d = MetaData()
        d['FILES'] = {}
        d['FILES']['${PN}'] = ['${base_bindir}', '${bindir}']
        d['FILES']['${PN}-doc'] = ['${docdir}']
        d['FILES']['${PN}-doc'].append_if['USE_foo'] = ['more']
        d['PN'] = 'foo'
        d['base_bindir'] = '/bin'
        d['docdir'] = '${datadir}/doc'
        d['datadir'] = '${prefix}/share'
        d['prefix'] = '/usr'
        d['bindir'] = '${prefix}/bin'
        d['FILES'].override_if['USE_foo'] = {}
        self.assertEqual(d['FILES'].get(),
                         {'foo': ['/bin', '/usr/bin'],
                          'foo-doc': ['/usr/share/doc']})
        d['OVERRIDES'] = ['USE_foo']
        self.assertEqual(d['FILES'].get(), {})

    def test_eval_duplicate(self):
        d = MetaData()
        d['FILES'] = {}
        d['FILES']['${PN}'] = ['/bin', '/usr/bin']
        d['FILES']['${PN}-doc'] = ['/usr/share/doc']
        d['FILES']['foo'] = ['/sbin', '/usr/sbin']
        d['PN'] = 'foo'
        self.assertRaises(MetaDataDuplicateDictKey, d['FILES'].get)

    def test_signature_1(self):
        d = MetaData()
        FOO = MetaVar(d, 'FOO', {'foo': 42, 'bar': 7})
        sig1 = str(FOO.signature())
        FOO['bar'] = 666
        sig2 = str(FOO.signature())
        FOO['bar'] = 7
        sig3 = str(FOO.signature())
        self.assertNotEqual(sig1, sig2)
        self.assertEqual(sig1, sig3)


class TestMetaBool(unittest.TestCase):

    def setUp(self):
        pass

    def test_init_metavar_true(self):
        d = MetaData()
        VAR = MetaVar(d, value=True)
        self.assertIsInstance(VAR, MetaBool)
        self.assertEqual(VAR.get(), True)

    def test_init_metavar_false(self):
        d = MetaData()
        VAR = MetaVar(d, value=False)
        self.assertIsInstance(VAR, MetaBool)
        self.assertEqual(VAR.get(), False)

    def test_init_none(self):
        d = MetaData()
        VAR = MetaBool(d, value=None)
        self.assertIsInstance(VAR, MetaBool)
        self.assertEqual(VAR.get(), None)

    def test_init_true(self):
        d = MetaData()
        VAR = MetaBool(d, value=True)
        self.assertIsInstance(VAR, MetaBool)
        self.assertEqual(VAR.get(), True)

    def test_init_false(self):
        d = MetaData()
        VAR = MetaBool(d, value=False)
        self.assertIsInstance(VAR, MetaBool)
        self.assertEqual(VAR.get(), False)

    def test_set_get_true(self):
        d = MetaData()
        VAR = MetaBool(d)
        VAR.set(True)
        self.assertEqual(VAR.get(), True)

    def test_set_get_false(self):
        d = MetaData()
        VAR = MetaBool(d)
        VAR.set(False)
        self.assertEqual(VAR.get(), False)

    def test_set_get_0(self):
        d = MetaData()
        VAR = MetaVar(d, value=True)
        self.assertRaises(TypeError, VAR.set, 0)

    def test_set_get_1(self):
        d = MetaData()
        VAR = MetaVar(d, value=True)
        self.assertRaises(TypeError, VAR.set, 1)

    def test_set_get_2(self):
        d = MetaData()
        VAR = MetaVar(d, value=True)
        self.assertRaises(TypeError, VAR.set, 2)

    def test_set_get_str(self):
        d = MetaData()
        VAR = MetaVar(d, value=True)
        self.assertRaises(TypeError, VAR.set, ('foobar'))

    def test_set_get_list(self):
        d = MetaData()
        VAR = MetaVar(d, value=True)
        self.assertRaises(TypeError, VAR.set, ([42]))

    def test_set_invalid_attr(self):
        d = MetaData()
        VAR = MetaVar(d, value=True)
        with self.assertRaises(AttributeError):
            VAR.foo = 'bar'

    def test_override_1(self):
        d = MetaData()
        VAR = MetaVar(d, value=True)
        d['OVERRIDES'] = ['USE_foo']
        VAR.override_if['USE_foo'] = False
        self.assertEqual(VAR.get(), False)

    def test_override_2(self):
        d = MetaData()
        VAR = MetaVar(d, value=False)
        d['OVERRIDES'] = ['USE_foo', 'USE_bar']
        VAR.override_if['USE_foo'] = True
        VAR.override_if['USE_bar'] = False
        self.assertEqual(VAR.get(), True)

    def test_str_true(self):
        d = MetaData()
        VAR = MetaVar(d, value=True)
        self.assertEqual(str(VAR), "True")

    def test_str_false(self):
        d = MetaData()
        VAR = MetaVar(d, value=False)
        self.assertEqual(str(VAR), "False")

    def test_weak_set_1(self):
        d = MetaData()
        FOO = MetaBool(d, 'FOO', True)
        FOO.weak_set(False)
        self.assertEqual(FOO.get(), True)

    def test_weak_set_2(self):
        d = MetaData()
        FOO = MetaBool(d, 'FOO', False)
        FOO.weak_set(True)
        self.assertEqual(FOO.get(), False)

    def test_weak_set_3(self):
        d = MetaData()
        FOO = MetaBool(d, 'FOO', None)
        FOO.weak_set(False)
        self.assertEqual(FOO.get(), False)

    def test_weak_set_4(self):
        d = MetaData()
        FOO = MetaBool(d, 'FOO', None)
        FOO.weak_set(True)
        self.assertEqual(FOO.get(), True)


class TestPythonExpression(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        e = PythonExpression('21 * 2')

    def test_repr(self):
        e = PythonExpression('21 * 2')
        self.assertEqual(repr(e), "PythonExpression('21 * 2')")

    def test_str(self):
        e = PythonExpression('21 * 2')
        self.assertEqual(str(e), "21 * 2")

    def test_code(self):
        e = PythonExpression('21 * 2')
        self.assertEqual(eval(e.code), 42)


class TestJSON(unittest.TestCase):

    def setUp(self):
        pass

    def test_1(self):
        src = MetaData()
        MetaVar(src, 'FOO', 'foo')
        dst = MetaData.loads(src.dumps())
        self.assertEqual(dst['FOO'].get(), 'foo')

    def test_appends(self):
        src = MetaData()
        MetaVar(src, 'FOO', 'foo')
        src['FOO'].append('bar')
        dst = MetaData.loads(src.dumps())
        self.assertEqual(dst['FOO'].get(), 'foobar')

    def test_prepends(self):
        src = MetaData()
        MetaVar(src, 'FOO', 'bar')
        src['FOO'].prepend('foo')
        dst = MetaData.loads(src.dumps())
        self.assertEqual(dst['FOO'].get(), 'foobar')

    def test_override_if_1(self):
        src = MetaData()
        MetaVar(src, 'FOO', 'foo')
        src['FOO'].override_if['USE_bar'] = 'bar'
        dst = MetaData.loads(src.dumps())
        dst['OVERRIDES'].append(['USE_bar'])
        self.assertEqual(src['FOO'].get(), 'foo')
        self.assertEqual(dst['FOO'].get(), 'bar')

    def test_override_if_2(self):
        src = MetaData()
        MetaVar(src, 'FOO', 'foo')
        src['FOO'].override_if['USE_bar'] = 'bar'
        src['FOO'].get()
        dst = MetaData.loads(src.dumps())
        dst['OVERRIDES'].append(['USE_bar'])
        self.assertEqual(src['FOO'].get(), 'foo')
        self.assertEqual(dst['FOO'].get(), 'bar')

    def test_prepend_if(self):
        src = MetaData()
        MetaVar(src, 'FOO', 'bar')
        src['FOO'].prepend_if['USE_bar'] = 'foo'
        dst = MetaData.loads(src.dumps())
        dst['OVERRIDES'].append(['USE_bar'])
        self.assertEqual(src['FOO'].get(), 'bar')
        self.assertEqual(dst['FOO'].get(), 'foobar')

    def test_append(self):
        src = MetaData()
        MetaVar(src, 'FOO', 'foo')
        src['FOO'].append_if['USE_bar'] = 'bar'
        dst = MetaData.loads(src.dumps())
        dst['OVERRIDES'].append(['USE_bar'])
        self.assertEqual(src['FOO'].get(), 'foo')
        self.assertEqual(dst['FOO'].get(), 'foobar')

    def test_signature_1(self):
        src = MetaData()
        MetaVar(src, 'FOO', 'foo')
        src_json = src.dumps()
        dst = MetaData.loads(src_json)
        self.assertEqual(src, dst)

    def test_signature_2(self):
        src = MetaData()
        MetaVar(src, 'FOO', 'foo')
        dst = MetaData.loads(src.dumps())
        src['FOO'].set('bar')
        self.assertNotEqual(src, dst)

    def test_signature_3(self):
        src = MetaData()
        MetaVar(src, 'FOO', 'foo')
        dst = MetaData.loads(src.dumps())
        src['FOO'].override_if['nothing'] = 'bar'
        self.assertNotEqual(src, dst)

    def test_signature_4(self):
        src = MetaData()
        MetaVar(src, 'FOO', 'foo')
        src['FOO'].override_if['nothing'] = 'bar'
        dst = MetaData.loads(src.dumps())
        self.assertEqual(src, dst)

    def test_signature_5(self):
        src = MetaData()
        MetaVar(src, 'FOO', 'foo')
        src['FOO'].override_if['nothing'] = 'bar'
        dst = MetaData.loads(src.dumps())
        self.assertEqual(src['FOO'].signature(), dst['FOO'].signature())
        self.assertEqual(src, dst)
        del src['FOO'].override_if['nothing']
        self.assertNotEqual(src, dst)

    def test_signature_6(self):
        src = MetaData()
        MetaVar(src, 'FOO', 'foo')
        src['FOO'].append_if['nothing'] = '1'
        src['FOO'].override_if['nothing'] = 'bar'
        src['FOO'].prepend_if['nothing'] = '2'
        dst = MetaData.loads(src.dumps())
        self.assertEqual(src, dst)
        del src['FOO'].append_if['nothing']
        self.assertNotEqual(src, dst)
        src['FOO'].append_if['nothing'] = '1'
        self.assertEqual(src, dst)

    def test_signature_7(self):
        src = MetaData()
        MetaVar(src, 'FOO', 'foo')
        src['FOO'].append_if['nothing'] = '1'
        src['FOO'].override_if['nothing'] = 'bar'
        src['FOO'].prepend_if['nothing'] = '2'
        dst = MetaData.loads(src.dumps())
        self.assertFalse(src != dst)
        del src['FOO'].append_if['nothing']
        self.assertTrue(src != dst)

    def test_signature_8(self):
        src = MetaData()
        MetaVar(src, 'FOO', 'foo')
        src['FOO'].append_if['nothing'] = '1'
        src['FOO'].override_if['nothing'] = 'bar'
        src['FOO'].prepend_if['nothing'] = '2'
        dst = MetaData.loads(src.dumps())
        self.assertTrue(src == dst)
        del src['FOO'].append_if['nothing']
        self.assertFalse(src == dst)
