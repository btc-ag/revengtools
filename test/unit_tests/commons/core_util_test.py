'''
Created on 19.05.2011

@author: SIGIESEC
'''
from commons.core_if import Adaptable
from commons.core_util import (PrefixMapper, StringTools, CollectionTools, 
    frozendict, IterTools, HierarchicalDecomposer, Grouper, DictReaderTools, 
    DefaultAdaptable, ClassTools)
from test.unit_tests.commons.testdata.config_tools_testdata import (
    ConcreteAutoConfigurableWithArgs)
import unittest

class StringToolsTest(unittest.TestCase):
    def test_strip_suffix_1(self):
        self.assertEquals('abcd', StringTools.strip_suffix("abcd", "BCD", ignore_case=False))

    def test_strip_suffix_2(self):
        self.assertEquals('a', StringTools.strip_suffix("abcd", "BCD", ignore_case=True))

    def test_strip_suffix_3(self):
        self.assertEquals('a', StringTools.strip_suffix("abcd", "bcd"))

    def test_strip_suffix_4(self):
        self.assertEquals('abcd', StringTools.strip_suffix("abcd", "xyz"))
        
    def test_strip_suffix_5(self):
        self.assertEquals('abcd', StringTools.strip_suffix("abcd", ""))
        
    def test_strip_suffix_6(self):
        self.assertEquals('', StringTools.strip_suffix("", ""))
        
    def test_strip_first_suffix_1(self):
        self.assertEquals('abc', StringTools.strip_first_suffix('abcd', ['d', 'c', 'b', 'a']))
        
    def test_strip_first_suffix_2(self):
        self.assertEquals('abc', StringTools.strip_first_suffix('abcd', ['a', 'b', 'c', 'd']))

    def test_strip_first_suffix_3(self):
        self.assertEquals('', StringTools.strip_first_suffix('', ['a', 'b', 'c', 'd']))
        
    def test_strip_first_suffix_non_fitting(self):
        self.assertEquals('abcd',StringTools.strip_first_suffix('abcd',['e','f','g','h']))
        
    def test_strip_first_suffix_none(self):
        self.assertEquals('abcd', StringTools.strip_first_suffix('abcd', []))

    def test_strip_suffixes_1(self):
        self.assertEquals('', StringTools.strip_suffixes('abcd', ['d', 'c', 'b', 'a']))

    def test_strip_suffixes_2(self):
        self.assertEquals('abc', StringTools.strip_suffixes('abcd', ['a', 'b', 'c', 'd']))
        
    def test_strip_all_suffixes_1(self):
        self.assertEquals('', StringTools.strip_all_suffixes('abcd', ['d', 'c', 'b', 'a']))

    def test_strip_all_suffixes_2(self):
        self.assertEquals('', StringTools.strip_all_suffixes('abcd', ['a', 'b', 'c', 'd']))

    def test_strip_all_suffixes_3(self):
        self.assertEquals('ab', StringTools.strip_all_suffixes('abcd', ['a', 'c', 'd']))
        
    def test_strip_all_suffixes_4(self):
        self.assertEquals('abcd', StringTools.strip_all_suffixes('abcd', ['a', 'b', 'c']))
        
    def test_strip_all_suffixes_none(self):
        self.assertEquals('abcd', StringTools.strip_all_suffixes('abcd', []))
        
    def test_strip_first_prefix_1(self):
        self.assertEquals('bcd', StringTools.strip_first_prefix('abcd', ['d', 'c', 'b', 'a']))
        
    def test_strip_first_prefix_2(self):
        self.assertEquals('bcd', StringTools.strip_first_prefix('abcd', ['a', 'b', 'c', 'd']))

    def test_strip_first_prefix_none(self):
        self.assertEquals('abcd', StringTools.strip_first_prefix('abcd', []))

    def test_strip_prefixes_1(self):
        self.assertEquals('bcd', StringTools.strip_prefixes('abcd', ['d', 'c', 'b', 'a']))

    def test_strip_prefixes_2(self):
        self.assertEquals('', StringTools.strip_prefixes('abcd', ['a', 'b', 'c', 'd']))
        
    def test_strip_all_prefixes_1(self):
        self.assertEquals('', StringTools.strip_all_prefixes('abcd', ['d', 'c', 'b', 'a']))

    def test_strip_all_prefixes_2(self):
        self.assertEquals('', StringTools.strip_all_prefixes('abcd', ['a', 'b', 'c', 'd']))
        
    def test_strip_all_prefixes_3(self):
        self.assertEquals('cd', StringTools.strip_all_prefixes('abcd', ['a', 'b', 'd']))
        
    def test_strip_all_prefixes_4(self):
        self.assertEquals('abcd', StringTools.strip_all_prefixes('abcd', []))
        
    def test_get_common_prefix_len_1(self):
        self.assertEquals(0, StringTools.get_common_prefix_len('', ''))
        
    def test_get_common_prefix_len_2(self):
        self.assertEquals(0, StringTools.get_common_prefix_len('a', ''))

    def test_get_common_prefix_len_3(self):
        self.assertEquals(0, StringTools.get_common_prefix_len('a', 'b'))
        
    def test_get_common_prefix_len_4(self):
        self.assertEquals(1, StringTools.get_common_prefix_len('a', 'a'))

    def test_get_common_prefix_len_5(self):
        self.assertEquals(1, StringTools.get_common_prefix_len('a', 'ab'))

    def test_get_common_prefix_len_6(self):
        self.assertEquals(2, StringTools.get_common_prefix_len('ab', 'ab'))
        
    def test_get_common_prefix_len_7(self):
        self.assertEquals(1, StringTools.get_common_prefix_len('ab', 'aB'))
        
    def test_get_common_prefix_len_8(self):
        self.assertEquals(0, StringTools.get_common_prefix_len('ab', 'Ab'))
        
    def test_get_common_prefix_1(self):
        self.assertEquals('ABC', StringTools.get_common_prefix(iter(('ABC', 'ABCD', 'ABCE'))))
        
    def test_get_common_prefix_2(self):
        self.assertEquals('', StringTools.get_common_prefix(set(('ABC', 'ABCD', 'ABCE', 'XYZ'))))

    def test_get_common_prefix_3(self):
        self.assertEquals('', StringTools.get_common_prefix(('dyn', 'prio4dyn', 'prid4dyn')))
    
    def test_get_common_prefix_4(self):
        self.assertEquals('', StringTools.get_common_prefix(('A', 'B')))
    
    def test_get_common_prefix_5(self):
        self.assertEquals(None, StringTools.get_common_prefix(()))
    
    def test_get_common_prefix_6(self):
        self.assertEquals((1, 2, 3), StringTools.get_common_prefix(((1,2,3),(1,2,3,4))))
        
    def test_optimise_prefix_strings(self):
        (prefix, optimised_map) = StringTools.prefix_optimise(("ABCD", "ABCE"))
        self.assertEquals('ABC', prefix)
        self.assertEquals([('ABCD', 'D'), ('ABCE', 'E')], sorted(optimised_map.iteritems()))
        
    def test_optimise_prefix_tuples(self):
        (prefix, optimised_map) = StringTools.prefix_optimise(((1, 2, 3), (1, 2, 4)))
        self.assertEquals((1,2), prefix)
        self.assertEquals([((1, 2, 3), (3,)), ((1, 2, 4), (4,))], sorted(optimised_map.iteritems()))
        
    def test_optimise_prefix_strings_null(self):
        (prefix, optimised_map) = StringTools.prefix_optimise(("ABCD", "XYZ"))
        self.assertEquals('', prefix)
        self.assertEquals([('ABCD', 'ABCD'), ('XYZ', 'XYZ')], sorted(optimised_map.iteritems()))
        
        
class IterToolsTest(unittest.TestCase):
    def test_sort_and_group_1(self):
        #>>> list((x, list(y)) for (x,y) in 
        self.assertEquals([('A', ['Abcd', 'Aloha']), ('B', ['Bar'])], 
                          [(x, list(y)) for (x,y) in IterTools.sort_and_group(lambda string: string[0], ('Abcd', 'Aloha', 'Bar'))])

    def test_sort_and_group_2(self):
        self.assertEquals([('A', ['Abcd', 'Aloha']), ('B', ['Bar'])], 
                          [(x, list(y)) for (x,y) in IterTools.sort_and_group(lambda string: string[0], ('Abcd', 'Aloha', 'Bar'))])

    def test_sort_and_group_null(self):
        self.assertEquals([], list(IterTools.sort_and_group(lambda x: x, ())))
        
    def test_sort_and_group_dicts_one_key(self):
        self.assertEquals([(0, [{'a': 0, 'b': 0}]), (1, [{'a': 1, 'b': 1}, {'a': 1, 'b': 2}])],
                          list((x, sorted(y)) for (x,y) in IterTools.sort_and_group_dicts('a', [{'a': 0, 'b': 0}, {'a': 1, 'b': 2}, {'a': 1, 'b': 1}])))
        
    def test_sort_and_group_dicts_two_keys(self):
        self.assertEquals([((0, 0), [{'a': 0, 'b': 0, 'c': 0}]), ((1, 0), [{'a': 1, 'b': 1, 'c': 0}, {'a': 1, 'b': 2, 'c': 0}])],
                          list((x, sorted(y)) for (x,y) in IterTools.sort_and_group_dicts(['a', 'c'], [{'a': 0, 'b': 0, 'c': 0}, {'a': 1, 'b': 2, 'c': 0}, {'a': 1, 'b': 1, 'c': 0}])))
        
    def test_sort_and_group_dicts_no_key(self):
        self.assertEquals([((), [{'a': 0, 'b': 0}, {'a': 1, 'b': 1}, {'a': 1, 'b': 2}])],
                          list((x, sorted(y)) for (x,y) in IterTools.sort_and_group_dicts([], [{'a': 0, 'b': 0}, {'a': 1, 'b': 2}, {'a': 1, 'b': 1}])))

    def test_sort_and_group_dicts_null(self):
        self.assertEquals([], list(IterTools.sort_and_group_dicts('a', [])))
        
    def test_sort_and_group_dicts_unknown_key(self):
        self.assertRaises(KeyError, IterTools.sort_and_group_dicts, 'a', [dict()])
        
    def test_quantify_1(self):
        self.assertEquals(0, IterTools.quantify([]))

    def test_quantify_2(self):
        self.assertEquals(0, IterTools.quantify([0]))

    def test_quantify_3(self):
        self.assertEquals(1, IterTools.quantify(iter([1])))
        
    def test_quantify_4(self):
        self.assertEquals(14, IterTools.quantify(range(15)))

    def test_count_1(self):
        self.assertEquals(0, IterTools.count([]))

    def test_count_2(self):
        self.assertEquals(1, IterTools.count([0]))

    def test_count_3(self):
        self.assertEquals(1, IterTools.count(iter([1])))

    def test_count_4(self):
        self.assertEquals(15, IterTools.count(range(15)))


    #TODO: Principal of analogy: Why before all assertions in a single method,
    #        but here all in one method?
    def test_first(self):
        testee = (x for x in range(2))
        self.assertEquals(0, IterTools.first(testee))
        self.assertEquals(1, IterTools.first(testee))
        self.assertRaises(StopIteration, IterTools.first, testee)
        self.assertEquals(0, IterTools.first(testee, 0))
        #self.assertEquals(None, IterTools.first(testee, None)) # TODO should this be possible?

class CollectionToolsTest(unittest.TestCase):
    def test_as_immutable_generator_expr(self):
        length = 3
        testee = (x for x in range(length))
        result = CollectionTools.as_immutable(testee)
        self.assertTrue(isinstance(result, tuple))
        self.assertNotEquals(id(testee), id(result))
        self.__check_len_twice(length, result)
        
    def test_as_immutable_tuple(self):
        length = 3
        testee = tuple(x for x in range(length))
        result = CollectionTools.as_immutable(testee)
        self.assertTrue(isinstance(result, tuple))
        self.assertEquals(id(testee), id(result))
        self.__check_len_twice(length, result)

    def test_as_immutable_list(self):
        length = 3
        testee = list(x for x in range(length))
        result = CollectionTools.as_immutable(testee)
        self.assertTrue(isinstance(result, tuple))
        self.assertNotEquals(id(testee), id(result))
        self.__check_len_twice(length, result)
        
    def test_as_immutable_set(self):
        length = 3
        testee = set(x for x in range(length))
        result = CollectionTools.as_immutable(testee)
        self.assertTrue(isinstance(result, frozenset))
        self.assertNotEquals(id(testee), id(result))
        self.__check_len_twice(length, result)
        
    def test_as_immutable_dict(self):
        length = 3
        testee = dict((x,x) for x in range(length))
        result = CollectionTools.as_immutable(testee)
        self.assertTrue(isinstance(result, frozendict))
        self.assertNotEquals(id(testee), id(result))
        self.__check_len_twice(length, result)
        
    def __check_len_twice(self, expected_len, iterable):
        self.assertEqual(expected_len, len(list(iterable)))
        self.assertEqual(expected_len, len(list(iterable)))
    
    def test_flatten_1(self):
        flat_iter = CollectionTools.flatten( (1,2,(3,(4,5))) )
        self.assertTrue(hasattr(flat_iter, "__iter__"))
        self.assertEquals([1, 2, 3, 4, 5], list(flat_iter))
        
    def test_flatten_2(self):
        flat_iter = CollectionTools.flatten( x for x in () )
        self.assertTrue(hasattr(flat_iter, "__iter__"))
        self.assertEquals([], list(flat_iter))

    def test_flatten_3(self):
        flat_iter = CollectionTools.flatten( ((), (), ()) )
        self.assertTrue(hasattr(flat_iter, "__iter__"))
        self.assertEquals([], list(flat_iter))


class PrefixMapperTest(unittest.TestCase):
    #TODO: uses other classes of core_util

    
    def setUp(self):
        self.__mapper = PrefixMapper(dict({'a': 1, 'ab': 2, '': 0}))
    
    def test_mapper_get_value_1(self):
        self.assertEquals(1, self.__mapper.get_value('ax'))

    def test_mapper_get_value_2(self):
        self.assertEquals(0, self.__mapper.get_value('bx'))    

    def test_mapper_get_value_3(self):
        self.assertEquals(2, self.__mapper.get_value('abx'))
        
    def test_mapper_get_value_4(self):
        self.assertEquals(1, self.__mapper.get_value('aB'))

    def test_get_value_None(self):
        self.assertEquals(None, self.__mapper.get_value(None))

class PrefixMapperEmptyTest(unittest.TestCase):
    def setUp(self):
        self.__mapper = PrefixMapper(dict())

    def test_get_value_1(self):
        self.assertEquals(None, self.__mapper.get_value('ax'))

    def test_get_value_None(self):
        self.assertEquals(None, self.__mapper.get_value(None))

class FrozenDictTest(unittest.TestCase):
    def get_source_dict(self):
        return dict({0:1, 1:2, 2:3})
    
    def get_source_dict_nested(self):
        return dict({0:[1,2,3], 1:[2,3,4], 2:[3,4]})

    def test_from_dict(self):
        source_dict = self.get_source_dict()
        target_dict = frozendict(source_dict)
        self.assertEquals(source_dict, target_dict)
        del source_dict[0]
        self.assertNotEquals(source_dict, target_dict)
        self.assertEquals([0] + source_dict.keys(), target_dict.keys())
        self.assertRaises(AttributeError, lambda: target_dict.pop)
        target_dict_2 = frozendict(target_dict)
        self.assertEquals(target_dict, target_dict_2) 
        
    def test_from_dict_nested(self):
        source_dict = self.get_source_dict_nested()
        target_dict = frozendict(source_dict)
        self.assertEquals(source_dict.keys(), target_dict.keys())
        for key in source_dict.keys():
            self.assertEquals(tuple(source_dict[key]), target_dict[key])
        target_dict_2 = frozendict(target_dict)
        self.assertEquals(target_dict, target_dict_2)
        self.assertEquals(hash(target_dict), hash(target_dict_2))
        self.assertNotEquals(hash(target_dict), hash(frozendict()))
            
    def test_direct(self):
        source_dict = dict(((0, [1,2,3]), (1,[2,3,4]), (2,[3,4])))
        target_dict = frozendict(((0, [1,2,3]), (1,[2,3,4]), (2,[3,4])))
        target_dict_2 = frozendict(target_dict)
        self.assertEquals(target_dict, target_dict_2) 
        self.assertEquals(source_dict.keys(), target_dict.keys())
        for key in source_dict.keys():
            self.assertEquals(tuple(source_dict[key]), target_dict[key], "dicts differ for key = %i" % key)
        
    def test_empty(self):
        target_dict = frozendict()
        self.assertEquals(0, len(target_dict))
        self.assertEquals(0, IterTools.quantify(target_dict.iteritems(), lambda x: 1))
        
class GrouperTest(unittest.TestCase):
    def test_grouper(self):
        grouper = Grouper(['b', 'a', '0'])
        grouper.add_group(lambda x: x.isalpha())
        self.assertEquals((('a', 'b'), ('0',)), tuple(tuple(sorted(x)) for x in grouper.get_groups()))

    def test_grouper_sorted(self):
        grouper = Grouper(['b', 'a', '0'], sort=True)
        grouper.add_group(lambda x: x.isalpha())
        self.assertEquals((('a', 'b'), ('0',)), grouper.get_groups())

    def test_grouper_remaining(self):
        grouper = Grouper(['b', 'a', '0'], sort=True)
        grouper.add_group(lambda x: x.isalpha())
        grouper.add_remaining()
        self.assertEquals((('a', 'b'), ('0',)), grouper.get_groups())
        self.assertRaises(RuntimeError, grouper.add_group, lambda x: True)

    def test_grouper_2(self):
        grouper = Grouper(['b', 'a', '0'], sort=True)
        grouper.add_group(lambda x: x.isalpha())
        grouper.add_group(lambda x: x.isdigit())
        grouper.add_remaining()
        self.assertEquals((('a', 'b'), ('0',)), grouper.get_groups())

    def test_grouper_3(self):
        grouper = Grouper(['b', 'a', '0'], sort=True)
        grouper.add_group(lambda x: x.isalpha())
        grouper.add_group(lambda x: False)
        grouper.add_remaining()
        self.assertEquals((('a', 'b'), (), ('0',)), grouper.get_groups())
    
    def test_grouper_4(self):
        grouper = Grouper(['0', 'b', 'a'], sort=True)
        grouper.add_group(lambda x: x.isalpha())
        grouper.add_group(lambda x: x.isdigit())
        grouper.add_remaining()
        self.assertEquals((('a', 'b'), ('0',)), grouper.get_groups())   
        
    def test_grouper_5(self):
        grouper = Grouper(['0', 'b', 'a','0'], sort=True)
        grouper.add_group(lambda x: x.isalpha())
        grouper.add_group(lambda x: x.isdigit())
        grouper.add_remaining()
        self.assertEquals((('a', 'b'), ('0',)), grouper.get_groups()) 
        
    def test_grouper_6(self):
        grouper = Grouper(['.', 'b', 'a','0'], sort=True)
        grouper.add_group(lambda x: x.isalpha())
        grouper.add_group(lambda x: x.isdigit())
        grouper.add_remaining()
        self.assertEquals((('a', 'b'), ('0',),('.',)), grouper.get_groups()) 
        
    def test_grouper_7(self):
        grouper = Grouper(['.', 'b', 'a','0'], sort=True)
        grouper.add_group(lambda x: x.isdigit())
        grouper.add_group(lambda x: x.isalpha())
        grouper.add_remaining()
        self.assertEquals((('0',),('a', 'b'),('.',)), grouper.get_groups()) 
                     
                     
class HierarchicalDecomposerTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.__decomposer = None
    
    def setUp(self):
        self.__decomposer = HierarchicalDecomposer(delimiter='.')
    
    def tearDown(self):
        self.__decomposer = None

    def test_decomposition_regular(self):
        self.assertEquals(("BTC", "CAB", "Commons", "Core"),
                          tuple(self.__decomposer.decompose("BTC.CAB.Commons.Core")))
        
    def test_decomposition_regular_with_empty_split(self):
        self.assertEquals(("BTC", "CAB", "", "Commons", "Core"),
                          tuple(self.__decomposer.decompose("BTC.CAB..Commons.Core")))
        
    def test_decomposition_no_delimiter(self):
        self.assertEquals(("BTC_CAB_Commons_Core", ),
                          tuple(self.__decomposer.decompose("BTC_CAB_Commons_Core")))

    def test_cluster_one_empty(self):
        self.assertEquals([], list(self.__decomposer.cluster_one_level([], None)))
        self.assertEquals([], list(self.__decomposer.cluster_one_level([], 0)))
        self.assertEquals([], list(self.__decomposer.cluster_one_level([], 3)))
       
    def test_cluster_basic_level_None(self):
        self.assertEquals(sorted([(('A.B.C', None), ['A.B.C']), (('A.B', None), ['A.B'])]), sorted(self.__decomposer.cluster_one_level(['A.B.C', 'A.B'], None)))


    #TODO: Is this the correct behavior?
    def test_cluster_basic_level_6(self):
        self.assertEquals(sorted([]), sorted(self.__decomposer.cluster_one_level(['A.B.C', 'A.B',''], 0)))

    def test_cluster_basic_level_5(self):
        self.assertEquals(sorted([(('A.B', 2), ['A.B.C']), (('B.A', 2), ['B.A'])]),
                           sorted(self.__decomposer.cluster_one_level(['A.B.C', 'B.A'], 2)))

    def test_cluster_basic_level_4(self):
        self.assertEquals(sorted([]), sorted(self.__decomposer.cluster_one_level(['A.B.C', 'A.B'], 4)))

    def test_cluster_basic_level_3(self):
        self.assertEquals(sorted([(('A.B.C', 3), ['A.B.C'])]), sorted(self.__decomposer.cluster_one_level(['A.B.C', 'A.B'], 3)))

    def test_cluster_basic_level_2(self):
        self.assertEquals(sorted([(('A.B', 2), ['A.B', 'A.B.C'])]), sorted(self.__decomposer.cluster_one_level(['A.B.C', 'A.B'], 2)))

    def test_cluster_basic_level_1(self):
        self.assertEquals(sorted([(('A', 1), ['A.B', 'A.B.C'])]), sorted(self.__decomposer.cluster_one_level(['A.B.C', 'A.B'], 1)))
                
    def test_limited_to_regular(self):
        self.assertEquals("BTC.CAB.Commons",
                          self.__decomposer.limited_to("BTC.CAB.Commons.Core", 3))

    def test_limited_to_shorter(self):
        self.assertEquals("BTC.CAB",
                          self.__decomposer.limited_to("BTC.CAB", 3))
        
    def test_limited_to_zero(self):
        self.assertEquals("",
                          self.__decomposer.limited_to("BTC.CAB", 0))
        
    def test_cluster_all_empty(self):
        self.assertEquals([], list(self.__decomposer.cluster_all_levels([])))

    def test_cluster_all_basic(self):
        self.assertEquals(sorted([(('A.B.C', None), ['A.B.C']), (('A.B', None), ['A.B']), (('A.B.C', 3), ['A.B.C']), (('A.B', 2), ['A.B', 'A.B.C']), (('A', 1), ['A.B', 'A.B.C'])]), 
                          sorted(self.__decomposer.cluster_all_levels(['A.B.C', 'A.B'])))
        
#    TODO: useful behaviour is unclear... raise Exception?
#    def test_decomposition_consecutive_delimiters(self):
#        self.assertEquals(("BTC_CAB_Commons_Core"),
#                          self.__decomposer.decompose("BTC..CAB.Commons.Core"))

        
class DictReaderToolsTest(unittest.TestCase):
    def test_transform_to_set_valued_dict_1(self):
        input_data = (dict({"key_column": "key1", "value_column": "value1"}), 
                      dict({"key_column": "key1", "value_column": "value2"}), 
                      dict({"key_column": "key2", "value_column": "value3", "foo": "bar"}))
        output = DictReaderTools.transform_to_set_valued_dict(input_data, "key_column", "value_column")
        self.assertEquals(["key1", "key2"], sorted(output.keys()))
        self.assertEquals(set(["value1", "value2"]), output["key1"])
        self.assertEquals(set(["value3"]), output["key2"])
        
class IUnitTestAsserter(object):        
    def assertTrue(self, assertThis):
        raise NotImplementedError(self.__class__)
        
class AdaptableTest(IUnitTestAsserter):
    def get_testee(self):
        raise NotImplementedError(self.__class__)
    
    def test_get_adaptees(self):
        testee = self.get_testee()
        self.assertTrue(testee.__class__ in testee.get_adaptees())

    def test_adapt_each(self):
        testee = self.get_testee()
        for adaptee_type in testee.get_adaptees():
            self.assertTrue(testee.adapt_to(adaptee_type))
            
    def test_adapt_all(self):
        testee = self.get_testee()
        adaptees = tuple(testee.get_adaptees())
        self.assertTrue(isinstance(testee.adapt_to(adaptees), adaptees[0]))
        reverse_adaptees = tuple(reversed(adaptees))
        self.assertTrue(isinstance(testee.adapt_to(reverse_adaptees), reverse_adaptees[0]))
        
class DefaultAdaptableTest(unittest.TestCase, AdaptableTest):
    def get_testee(self):
        return DefaultAdaptable()
    
    def test_get_adapters_default(self):
        testee = self.get_testee()
        self.assertEquals([DefaultAdaptable, Adaptable, object], list(testee.get_adaptees()))


class ConcreteAutoConfigurableWithArgsSubclass(ConcreteAutoConfigurableWithArgs):
    pass


    #TODO: Why are there errors marked?

class ClassToolsTest(unittest.TestCase):
    def test_get_constructor(self):
        constructor = ClassTools.get_constructor(ConcreteAutoConfigurableWithArgs)
        self.assertTrue(constructor != None)
        self.assertEquals("__init__", constructor.__name__)
        self.assertEquals(ConcreteAutoConfigurableWithArgs.__init__.im_func, constructor)

    def test_get_constructor_superclass(self):
        constructor = ClassTools.get_constructor(ConcreteAutoConfigurableWithArgsSubclass)
        self.assertTrue(constructor != None)
        self.assertEquals("__init__", constructor.__name__)
        self.assertEquals(ConcreteAutoConfigurableWithArgs.__init__.im_func, constructor)

    def test_get_constructor_fail(self):
        constructor = ClassTools.get_constructor(object)
        self.assertTrue(constructor == None)
    
    def test_get_constructor_args(self):
        self.assertEquals(["testarg", "defarg"], 
                          list(ClassTools.get_constructor_args(ConcreteAutoConfigurableWithArgs)))
        
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_']
    unittest.main()
