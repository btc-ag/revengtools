#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Extension functionality around basic Python data structures.

This module depends only on standard python modules, both directly and indirectly. 

Created on 07.07.2010

@author: Simon Giesecke
@author: Martin Migasiewicz
'''
from __future__ import with_statement
from commons.core_if import Adaptable
from commons.v26compat_util import (compatchain, compatnext, is_iterable, 
    OrderedDict)
from functools import partial
from itertools import imap, ifilter, izip, tee, chain, groupby, takewhile
from collections import defaultdict
import inspect
import pprint #@UnusedImport#
import re
import itertools
import types

#
# Extended version of ASPN's Python Cookbook Recipe:
# Frozen dictionaries.
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/414283
#
# This version freezes dictionaries used as values within dictionaries.
#
class frozendict(dict):
    def _blocked_attribute(self):
        raise AttributeError, "A frozendict cannot be modified."
    _blocked_attribute = property(_blocked_attribute)

    __delitem__ = __setitem__ = clear = _blocked_attribute
    pop = popitem = setdefault = update = _blocked_attribute

    @staticmethod
    def __get_frozen(arg, start=True):
        if isinstance(arg, frozendict):
            return arg
        elif isinstance(arg, dict):
            if start:
                return izip(arg.iterkeys(), imap(frozendict.__get_frozen, arg.itervalues()))
            else:
                return frozendict(arg)
        elif isinstance(arg, list) or isinstance(arg, tuple):
            return tuple(imap(frozendict.__get_frozen, arg))
        else:
            return arg

    def __new__(cls, *args, **kw):
        new = dict.__new__(cls)

        args_ = []
        for arg in args:
            args_.append(cls.__get_frozen(arg))

        dict.__init__(new, *args_, **kw)
        return new

    def __init__(self, *args, **kw):
        pass

    def __hash__(self):
        try:
            return self._cached_hash
        except AttributeError:
            h = self._cached_hash = hash(tuple(sorted(self.items())))
            return h

    def __repr__(self):
        return "frozendict(%s)" % dict.__repr__(self)

class List(list):
    """
    Specialization of list for use in weak references.
    """

    pass

class StringTools(object):
    """
    Static extension methods for string-like objects. 
    """
    
    @staticmethod
    def strip_suffix(string, suffix, ignore_case=False):
        """
        >>> StringTools.strip_suffix("abcd", "BCD", ignore_case=False)
        'abcd'
        >>> StringTools.strip_suffix("abcd", "BCD", ignore_case=True)
        'a'
        >>> StringTools.strip_suffix("abcd", "bcd")
        'a'
        >>> StringTools.strip_suffix("abcd", "xyz")
        'abcd'
        >>> StringTools.strip_suffix("abcd", "")
        'abcd'
        """
        if (not ignore_case and string.endswith(suffix)) or \
            (ignore_case and string.lower().endswith(suffix.lower())):
            return string[:len(string) - len(suffix)]
        else:
            return string

    @classmethod
    def strip_suffixes(cls, string, suffixes, ignore_case=False, strip_func=None):
        """
        
        @param string:
        @param suffixes:
        @param ignore_case:
        @deprecated: use either StringTools.strip_first_suffix or StringTools.strip_all_suffixes, 
          depending on the required semantics
        """
        # TODO deprecate and replace by strip_one_suffix/strip_all_suffixes
        if not strip_func:
            strip_func = cls.strip_suffix
        result = string
        for suffix in suffixes:
            result = strip_func(result, suffix, ignore_case=ignore_case)
        return result

    @classmethod
    def strip_first_suffix(cls, string, suffixes, ignore_case=False, strip_func=None):
        """
        For each of several strings, checks whether they are a suffix of a given string; 
        on the first match, strip that suffix and return the result.          
        """
        if not strip_func:
            strip_func = cls.strip_suffix
        for suffix in suffixes:
            result = strip_func(string, suffix, ignore_case=ignore_case)
            if len(result) != len(string):
                return result
        return string

    @classmethod
    def strip_all_suffixes(cls, string, suffixes, ignore_case=False, strip_func=None):
        if not strip_func:
            strip_func = cls.strip_suffix
        prev_len = len(string) + 1
        curr = string
        while prev_len > len(curr):
            prev_len = len(curr)
            for suffix in suffixes:
                curr = strip_func(curr, suffix, ignore_case=ignore_case)
        return curr

    @staticmethod
    def strip_prefix(string, suffix, ignore_case=False):
        """
        >>> StringTools.strip_prefix("abcd", "abc")
        'd'
        >>> StringTools.strip_prefix("abcd", "xyz")
        'abcd'
        >>> StringTools.strip_prefix("abcd", "")
        'abcd'
        """
        if ignore_case:
            raise NotImplementedError("ignore_case not implemented for strip_prefix")
        if string.startswith(suffix):
            return string[len(suffix):]
        else:
            return string

    @staticmethod
    def strip_prefixes(string, prefixes):
        return StringTools.strip_suffixes(string, prefixes, strip_func=StringTools.strip_prefix)

    @staticmethod
    def strip_first_prefix(string, prefixes):
        return StringTools.strip_first_suffix(string, prefixes, strip_func=StringTools.strip_prefix)

    @staticmethod
    def strip_all_prefixes(string, prefixes):
        return StringTools.strip_all_suffixes(string, prefixes, strip_func=StringTools.strip_prefix)

    @staticmethod
    def stringify(string_list):
        """
        Takes as parameter a string that contains strings separated by a comma
        (can contain also only one element) and checks if strings are surrounded 
        with apostrophes
        
        Example:
          "a string without apostrophes", "'string in apostrophes'"
          stringified_list = stringify( list )
          #stringified_list = "'a string without apostrophes'", "'string in apostrophes'"   

        >>> StringTools.stringify( "hello" )
        "'hello'"
        >>> StringTools.stringify( "hello world" )
        "'hello world'"
        >>> StringTools.stringify( "'Hello World', the quick brown fox jumps over the lazy dog" )
        "'Hello World','the quick brown fox jumps over the lazy dog'"
        >>> StringTools.stringify( "'hello', world" )
        "'hello','world'"
        """
        pattern = r"\'\w+\s*\w+\'"
        argument = string_list

        values = argument.split(",")
        argument = ""
        last_index = len(values) - 1

        for i, item in enumerate(values) :
            item = item.strip()
            if not re.search(pattern, item) :
                item = "'" + item + "'"
            argument += item
            if i != last_index :
                argument += ","

        return argument

    @staticmethod
    def get_common_prefix_len(string1, string2):
        """
        Returns the number of starting characters shared by string1 and string2.
        
        @param string1: a string (in fact, any subscriptable object)
        @param string2: a string (in fact, any subscriptable object)
        @return a non-negative integer
        
        >>> StringTools.get_common_prefix_len('', '')
        0
        >>> StringTools.get_common_prefix_len('a', '')
        0
        >>> StringTools.get_common_prefix_len('a', 'b')
        0
        >>> StringTools.get_common_prefix_len('a', 'a')
        1
        >>> StringTools.get_common_prefix_len('a', 'ab')
        1
        >>> StringTools.get_common_prefix_len('ab', 'ab')
        2
        >>> StringTools.get_common_prefix_len('ab', 'aB')
        1
        >>> StringTools.get_common_prefix_len('ab', 'Ab')
        0
        """
        return IterTools.quantify(takewhile(lambda (a, b): a == b, izip(string1, string2)), lambda x: 1)
        # previous version... which is more efficient?
#        shorterLength = min(len(string1), len(string2))
#        for i in range(0, shorterLength):
#            if string1[i] != string2[i]:
#                return i
#        return shorterLength

    @staticmethod
    def get_common_prefix(stringIter):
        """
        Returns the longest common prefix of all strings in stringIter.
        In fact, the elements of stringIter do not need to be strings, they 
        just need to be subscriptable.
        
        @param stringIter: an iterable containing subscriptable elements
        @return a string, or None if stringIter is empty
        
        >>> StringTools.get_common_prefix(iter(('ABC', 'ABCD', 'ABCE')))
        'ABC'
        >>> StringTools.get_common_prefix(set(('ABC', 'ABCD', 'ABCE', 'XYZ')))
        ''
        >>> StringTools.get_common_prefix(('dyn', 'prio4dyn', 'prid4dyn'))
        ''
        >>> StringTools.get_common_prefix(('A', 'B'))
        ''
        >>> StringTools.get_common_prefix(())
        >>> StringTools.get_common_prefix(((1,2,3),(1,2,3,4)))
        (1, 2, 3)
        """
        commonPrefix = None
        for string in stringIter:
            if commonPrefix == None:
                commonPrefix = string
            else:
                commonCount = StringTools.get_common_prefix_len(string, commonPrefix)
                commonPrefix = commonPrefix[:commonCount]

        return commonPrefix

    @staticmethod
    def prefix_optimise(input_sequences):
        """
        Determines the (longest) common prefix of some input sequences and a map of the input 
        sequences to sequences where the common prefix has been stripped.   

        An example using strings:
        >>> (prefix, optimised_map) = StringTools.prefix_optimise(("ABCD", "ABCE"))
        >>> prefix
        'ABC'
        >>> sorted(optimised_map.iteritems())
        [('ABCD', 'D'), ('ABCE', 'E')]

        An example using integer tuples:
        >>> (prefix, optimised_map) = StringTools.prefix_optimise(((1, 2, 3), (1, 2, 4)))
        >>> prefix
        (1, 2)
        >>> sorted(optimised_map.iteritems())
        [((1, 2, 3), (3,)), ((1, 2, 4), (4,))]

        In this case, the common prefix is empty, so no optimisation is possible: 
        >>> (prefix, optimised_map) = StringTools.prefix_optimise(("ABCD", "XYZ"))
        >>> prefix
        ''
        >>> sorted(optimised_map.iteritems())
        [('ABCD', 'ABCD'), ('XYZ', 'XYZ')]
        """
        common_prefix = StringTools.get_common_prefix(input_sequences)

        optimised_sequences = dict()
        for input_sequence in input_sequences:
            optimised_sequences[input_sequence] = input_sequence[len(common_prefix):]

        return common_prefix, optimised_sequences

    
    @classmethod
    def shortest_of(cls, strings_iterable):
        """
        >>> StringTools.shortest_of([])
        >>> StringTools.shortest_of(['a'])
        'a'
        >>> StringTools.shortest_of(['abc', 'a', 'ab'])
        'a'
        >>> StringTools.shortest_of(['a', 'b'])
        'a'
        """
        try:
            strings_iter = iter(strings_iterable)
            result = next(strings_iter)
            for string in strings_iter:
                if len(string) < len(result):
                    result = string
            return result
        except StopIteration:
            return None

    @classmethod
    def longest_of(cls, strings_iterable):
        try:
            strings_iter = iter(strings_iterable)
            result = next(strings_iter)
            for string in strings_iter:
                if len(string) > len(result):
                    result = string
            return result
        except StopIteration:
            return None

class IterTools(object):
    @staticmethod
    def sort_and_group(key_func, iterable):
        """
        Returns an iterator of groups in an iterable according to a key function
        and is similar to SQL’s GROUP BY.  
        
        @see: itertools.groupby for the result format 
        
        @see: IterTools.sort_and_group_dicts can be used more conveniently if the elements of 
            iterable are dictionaries
            
        @param key_func: a function that can be applied to the elements of iterable  
        
        >>> list((x, list(y)) for (x,y) in IterTools.sort_and_group(lambda string: string[0], ('Abcd', 'Aloha', 'Bar')))
        [('A', ['Abcd', 'Aloha']), ('B', ['Bar'])]
        """
        return groupby(sorted(iterable, key=key_func), key=key_func)

    @staticmethod
    def sort_and_group_dicts(key_column, input_data):
        """
        
        @see: itertools.groupby for the result format 

        @param key_column: a key or an iterable of keys of the input data
        @param input_data: an iterable of dictionaries, each of which is required to have the key(s) specified by key_columns

        >>> list((x, sorted(y)) for (x,y) in IterTools.sort_and_group_dicts('a', [{'a': 0, 'b': 0}, {'a': 1, 'b': 2}, {'a': 1, 'b': 1}]))
        [(0, [{'a': 0, 'b': 0}]), (1, [{'a': 1, 'b': 1}, {'a': 1, 'b': 2}])]
        """
        if hasattr(key_column, "__iter__") and not isinstance(key_column, basestring):
            key_func = lambda x: tuple(x[column] for column in key_column)
        else:
            key_func = lambda x: x[key_column]
        return IterTools.sort_and_group(key_func, input_data)

    @classmethod
    def quantify(cls, iterable, pred=bool):
        """
        >>> IterTools.quantify([])
        0
        
        >>> IterTools.quantify([0])
        0
        
        >>> IterTools.quantify([5, 10, 15])
        3

        >>> IterTools.quantify([5, 10, 15], lambda x: x>5)
        2

        >>> IterTools.quantify([5, 10, 15], lambda x: x)
        30
        """
        return sum(imap(pred, iterable))

    @staticmethod
    def first(iterable, default=None):
        """
        Returns the first item or a default value.
        
        #>>> IterTools.first([]) # raises a StopIteration exception
        >>> IterTools.first([], 1)
        1
        >>> IterTools.first(iter(['a']))
        'a'
        """
        return compatnext(iter(iterable), default)

    count = None

IterTools.count = partial(IterTools.quantify, pred=lambda x: 1)

class CollectionTools(object):
    """
    Extension methods for collections.
    
    See also IterTools for more general extension methods that depend only on iterables/iterators.
    """
        
    @staticmethod
    def as_immutable(iterable):
        """
        Returns the iterable as an immutable collection. 
        
        Implementation notes: Optimized not to make a copy of the iterable if 
          it already is of a known type of immutable collection. Currently,
          known immutable collection types include tuple, frozenset and frozendict.
        
        @rtype: An immutable collection (frozenset for a set, frozendict for a dict, tuple else)    
        """
        if isinstance(iterable, (types.TupleType, frozenset, frozendict)):
            return iterable
        elif isinstance(iterable, set):
            return frozenset(iterable)
        elif isinstance(iterable, dict):
            return frozendict(iterable)
        return tuple(iterable)

    @staticmethod
    def flatten(iterable):
        """
        Generates an iterator that iterates through a possibly nested 
        structure of iterators (typically collections) and makes them 
        appear as a flat list.
        
        Similar to itertools.chain but flattens an arbitrary number of levels.  
    
        >>> list(CollectionTools.flatten( (1,2,(3,(4,5))) ))
        [1, 2, 3, 4, 5]
        """
        # TODO Should be moved to IterTools
        for element in ifilter(None, iterable):
            if is_iterable(element) and not isinstance(element, basestring):
                for sub_element in CollectionTools.flatten(element):
                    yield sub_element
            else:
                yield element

    @staticmethod
    def union_all(iterables):
        """
        >>> sorted(CollectionTools.union_all([[1, 2], [2, 3]]))
        [1, 2, 3]
        >>> sorted(CollectionTools.union_all([(1, 2), (2, 3)]))
        [1, 2, 3]
        >>> sorted(CollectionTools.union_all([((1, 2), (2, 3),)]))
        [(1, 2), (2, 3)]
        """
#        result = set()
#        for iterable in iterables:
#            result.update(iterable)
#            
#        return result
        # TODO ist das effizienter als
        return set(compatchain.from_iterable(iterables))

    @staticmethod
    def concat_all(iterables):
        """
        >>> CollectionTools.concat_all([[1, 2], [2, 3]])
        [1, 2, 2, 3]
        """
        return list(compatchain.from_iterable(iterables))


    @staticmethod
    def transpose_items_as_dict(itemlist):
        """
        >>> CollectionTools.transpose_items_as_dict([(1, 2), (3, 4)])
        {2: 1, 4: 3}
        """
        return dict((x[1], x[0]) for x in itemlist)

    @staticmethod
    def value_set_to_tuple(inDictionary):
        """
        Takes a set-of-strings-valued inDictionary and returns a new inDictionary with tuple values sorted
        by elements.
        
        >>> CollectionTools.value_set_to_tuple({'x': set(['a', 'b'])})
        {'x': ('a', 'b')}
    
        >>> CollectionTools.value_set_to_tuple({'x': set([])})
        {'x': ()}
        """
        outDictionary = dict()
        for key in inDictionary:
            outDictionary[key] = tuple(sorted(inDictionary[key]))
        return outDictionary

    @staticmethod
    def value_tuple_to_set(inDictionary):
        """
        
        @param inDictionary:
        @type inDictionary:
        """
        outDictionary = dict()
        for key in inDictionary:
            outDictionary[key] = set(inDictionary[key])
        return outDictionary


    @staticmethod
    def transpose(inDictionary):
        """
        Returns a transposed dictionary, i.e. values and keys are exchanged. 
        Keys in the in dictionary with the same values are concatenated into 
        a sorted tuple.
        
        >>> CollectionTools.transpose({})
        {}
        
        >>> CollectionTools.transpose({'a': ('x',)})
        {('x',): ('a',)}
    
        >>> CollectionTools.transpose({'a': ('x',), 'b': ('x',)})
        {('x',): ('a', 'b')}
    
        >>> CollectionTools.transpose({'a': ('x',), 'b': ('y',)})
        {('y',): ('b',), ('x',): ('a',)}
        """
        outDictionary = dict()
        # TODO das sieht irgendwie ineffizient aus
        for pair in izip(inDictionary.itervalues(), inDictionary.iterkeys()):
            oldValue = outDictionary.get(pair[0], [])
            outDictionary[pair[0]] = tuple(sorted(chain(oldValue, [pair[1]])))
        return outDictionary


    @staticmethod
    def find_duplicates(iterator, ignore=lambda x: len(x) == 0):
        """
        Returns a list of duplicates in a given iterator. Certain elements may be 
        ignored in checking for duplicates. By default elements with zero length 
        are ignored. If elements are no iterables, call 
        find_duplicates(iterator, lambda x: 0).
        
        >>> len(CollectionTools.find_duplicates([]))
        0
    
        >>> sorted(CollectionTools.find_duplicates(['a', 'b', 'c']))
        []
        
        >>> sorted(CollectionTools.find_duplicates(['a', 'a', 'b']))
        ['a']
    
        >>> sorted(CollectionTools.find_duplicates(['a', 'a', 'a']))
        ['a']
    
        >>> len(CollectionTools.find_duplicates(['', '', 'a']))
        0
        
        >>> sorted(CollectionTools.find_duplicates([1,1,2,2,3], lambda x: False))
        [1, 2]
        """
        sorted_list = sorted(iterator)
        previous = None
        duplicates = set()
        for current in sorted_list:
            if not ignore(current):
                if current == previous:
                    duplicates.add(current)
                else:
                    previous = current
        return duplicates

    @staticmethod
    def find_duplicate_values(itemiterator, ignore=lambda x: len(x) == 0):
        """
        Determines duplicate values in a list of (key,value)-tuples and 
        returns a dictionary mapping duplicate values to a set of their keys.
        
        >>> CollectionTools.find_duplicate_values([('c', 'x'), ('a', 'y'), ('b', 'y')])
        {'y': set(['a', 'b'])}
        """
        my_dict = dict()
        for (a, b) in itemiterator:
            if not ignore(b):
                if b in my_dict:
                    my_dict[b].add(a)
                else:
                    my_dict[b] = set([a])
        result_dict = dict()
        for key in my_dict.iterkeys():
            if len(my_dict[key]) > 1:
                result_dict[key] = my_dict[key]
        return result_dict

    @staticmethod
    def identity_dict(iterable):
        """
        >>> CollectionTools.identity_dict(iter(['a']))
        {'a': 'a'}
        """
        return dict(izip(*tee(iterable)))
    
    @staticmethod
    def extend_unique_slow(result, inputs):
        """
        Extends a list similar to the extend method, but add only elements that are not 
        yet in the list.
        
        This implementation operates with O((m+n)^2) complexity where m and n 
        are the number of elements of the two parameters, but requires no additional memory.
        It is faster than extend_unique in the worst case (all elements are different) 
        up to about m+n=25 (using CPython 2.6.6).    
        
        >>> CollectionTools.extend_unique_slow([], [])
        []
        
        >>> CollectionTools.extend_unique_slow([], [1, 2, 3])
        [1, 2, 3]

        >>> CollectionTools.extend_unique_slow([3, 2, 1], [1, 2, 3])
        [3, 2, 1]

        >>> CollectionTools.extend_unique_slow([], [1, 2, 3, 3, 2, 1])
        [1, 2, 3]
        """
        for element in inputs:
            if element not in result:
                result.append(element)
        return result

    @staticmethod
    def extend_unique(result, inputs):
        """
        Extends a list similar to the extend method, but add only elements that are not 
        yet in the list.
        
        This implementation operates with O((m+n)log (m+n)) complexity where m and n 
        are the number of elements of the two parameters.   
        
        >>> CollectionTools.extend_unique([], [])
        []
        
        >>> CollectionTools.extend_unique([], [1, 2, 3])
        [1, 2, 3]

        >>> CollectionTools.extend_unique([3, 2, 1], [1, 2, 3])
        [3, 2, 1]

        >>> CollectionTools.extend_unique([], [1, 2, 3, 3, 2, 1])
        [1, 2, 3]
        """
        #if hasattr(inputs, "__len__") and (len(result) + len(inputs)) < 30:
        #    return CollectionTools.extend_unique_slow(result, inputs)
        element_keys = set(result)
        for element in inputs:
            if element not in element_keys:
                element_keys.add(element)
                result.append(element)
        return result
        
    @staticmethod
    def extend_unique_keys(result, inputs, keyfunc):
        """
        Extends a list similar to the extend method, but add only elements that are not 
        yet in the list.
        
        This implementation operates with O((m+n)log (m+n)) complexity where m and n 
        are the number of elements of the two parameters.   
        
        >>> CollectionTools.extend_unique_keys([], [], keyfunc=len)
        []
        
        >>> CollectionTools.extend_unique_keys([], ["A", "AB", "ABC"], keyfunc=len)
        ['A', 'AB', 'ABC']

        >>> CollectionTools.extend_unique_keys(["ABC", "AB", "A"], ["a", "ab", "abc"], keyfunc=len)
        ['ABC', 'AB', 'A']

        >>> CollectionTools.extend_unique_keys([], ["b", "a", "ab", "abc", "cba", "bb"], keyfunc=len)
        ['b', 'ab', 'abc']
        """
        if keyfunc==None:
            return CollectionTools.extend_unique(result, inputs)
        element_keys = set(imap(keyfunc, result))
        for element in inputs:
            element_key = keyfunc(element)
            if element_key not in element_keys:
                element_keys.add(element_key)
                result.append(element)
        return result

class SetValuedDictTools(object):
    """
    A collection of tools to handle set-valued dicts, i.e. dictionaries where the values are sets, 
    and the keys are (treated as) scalars.
    """
    @staticmethod
    def transpose(inDictionary):
        """
        Converts a A-to-set(B)-valued-dictionary to a B-to-set(A)-dictionary.
        
        @rtype: defaultdict(set)
        
        >>> pprint.pprint(dict(SetValuedDictTools.transpose({'x': set(['a', 'b']), 'y': set(['c'])})))
        {'a': set(['x']), 'b': set(['x']), 'c': set(['y'])}
        """
        allValues = set(compatchain.from_iterable(inDictionary.itervalues()))
        transposedDictionary = defaultdict(set)
        for value in allValues:
            #transposedDictionary.update({value: set()})
            for key in inDictionary:
                if value in inDictionary[key]:
                    transposedDictionary[value].add(key)
        return transposedDictionary

    @staticmethod
    def convert_from_itemiterator(itemiterator):
        """
        Converts a list of (key,value)-tuples to a set-valued dictionary.
        
        @rtype: defaultdict(set)

        >>> dict(SetValuedDictTools.convert_from_itemiterator([]))
        {}
        
        >>> dict(SetValuedDictTools.convert_from_itemiterator([('a', 'b'), ('a', 'c')]))
        {'a': set(['c', 'b'])}
        """
        result_dict = defaultdict(set)
        for key, val in itemiterator:
            result_dict[key].add(val)

        return result_dict

    @staticmethod
    def join_keys(dictionary, targetKey, sourceKeys):
        """
        Joins the values of the specified source keys in the dictionary into the target key, 
        which may or may not exist previously.
        
        >>> SetValuedDictTools.join_keys({}, 'x', ['y'])
        {}
    
        >>> pprint.pprint(SetValuedDictTools.join_keys({'x': set(['a', 'b']), 'y': set(['c'])}, 'x', ['y']))
        {'x': set(['a', 'b', 'c'])}
        
        >>> pprint.pprint(SetValuedDictTools.join_keys({'x': set(['a', 'b']), 'y': set(['c'])}, 'x', ['y']))
        {'x': set(['a', 'b', 'c'])}
        
        >>> pprint.pprint(SetValuedDictTools.join_keys({'x': set(['a', 'b']), 'y': set(['c'])}, 'x', ['z']))
        {'x': set(['a', 'b']), 'y': set(['c'])}
        
        >>> pprint.pprint(SetValuedDictTools.join_keys({frozenset(['x']): set(['a', 'b']), frozenset(['y']): set(['c'])}, frozenset(['x']), [frozenset(['z'])]))
        {frozenset(['y']): set(['c']), frozenset(['x']): set(['a', 'b'])}
        """
        if targetKey not in dictionary:
            dictionary.update(dict({targetKey: set('')}))
        for sourceKey in sourceKeys:
            if sourceKey in dictionary:
                dictionary[targetKey] |= set(dictionary[sourceKey])
                if targetKey != sourceKey:
                    del dictionary[sourceKey]
        if len(dictionary[targetKey]) == 0:
            del dictionary[targetKey]
        return dictionary

    @staticmethod
    def add_or_create(dictionary, key, value_element):
        """
        Creates a set for a key in the dictionary if it does not exist, and adds a value element to the set.
        
        @deprecated: no longer necessary, use defaultdict(set) instead of dict
        
        @return: the dictionary
        @rtype: dict
        
        >>> d = dict()
        >>> SetValuedDictTools.add_or_create(d, 1, 100)
        {1: set([100])}
        >>> SetValuedDictTools.add_or_create(d, 1, 200)
        {1: set([200, 100])}
        """
        if key not in dictionary:
            dictionary[key] = set()
        dictionary[key].add(value_element)
        return dictionary

class Grouper(object):
    """
    @rtype: tuple of tuples of the input elements.
    
    >>> grouper = Grouper(['a', 'b', '0'])
    >>> grouper.add_group(lambda x: x.isalpha())
    >>> grouper.get_groups()
    (('a', 'b'), ('0',))
    """

    # TODO preserve order of the input elements?

    def __init__(self, input_elements, sort=False):
        self.__groups = []
        self.__sort = sort
        self.__unprocessed = set(input_elements)

    def __add_group_raw(self, items):
        if self.__sort:
            items = sorted(items)
        self.__groups.append(tuple(items))

    def add_group(self, filter_func):
        if self.__unprocessed != None:
            selected = filter(filter_func, self.__unprocessed)
            self.__add_group_raw(selected)
            self.__unprocessed.difference_update(selected)
        else:
            raise RuntimeError("called add_group after add_remaining")

    def add_remaining(self):
        if self.__unprocessed and len(self.__unprocessed):
            self.__add_group_raw(self.__unprocessed)
        self.__unprocessed = None

    def get_groups(self):
        self.add_remaining()
        return tuple(self.__groups)

class SuffixMapper(object):
    """
    >>> mapper = SuffixMapper(dict({'_a': 1, '_ab': 2, '': 0}))
    >>> mapper.get_value('x_a')
    1
    >>> mapper.get_value('x_b')
    0
    >>> mapper.get_value('x_ab')
    2
    """

    def __init__(self, suffix_to_value_map):
        # TODO kann man das nicht auch als Klassenvariable machen?
        self.__internal_module_suffixes = sorted(suffix_to_value_map.iteritems(),
                                                 key=lambda item:-len(item[0]))

    def get_value(self, query_key):
        for (suffix, value) in self.__internal_module_suffixes:
            if query_key.endswith(suffix):
                return value
        return None

class PrefixMapper(object):
    """
    Based on a dictionary of prefixes to values, the get_value method will determine 
    the longest prefix and return the associated value. A default value can be specified 
    by adding a value for the empty string to the prefix_to_value_map. 
    
    >>> mapper = PrefixMapper(dict({'a': 1, 'ab': 2, '': 0}))
    >>> mapper.get_value('ax')
    1
    >>> mapper.get_value('bx')
    0
    >>> mapper.get_value('abx')
    2
    """

    def __init__(self, prefix_to_value_map):
        self.__internal_module_suffixes = sorted(prefix_to_value_map.iteritems(),
                                                 key=lambda item:-len(item[0]))

    def get_value(self, query_key):
        """
        Determines the longest prefix of query_key among the prefixes of this object and 
        returns the value associated with it.
        
        @param query_key: a key, or None
        @return: a value, or None if query_key is None or if no prefix in the associated prefix_to_value_map matches
        """
        if query_key != None:
            try:
                return IterTools.first(value
                                       for (prefix, value) in self.__internal_module_suffixes
                                       if query_key.startswith(prefix))
            except StopIteration:
                return None
        else:
            return None

class HierarchicalDecomposer(object):
    def __init__(self, delimiter):
        self.__delimiter = delimiter
        
    def cluster_one_level(self, input_strings, level):
        if level == None:
            return (((string, None), [string]) for string in input_strings)
        else:
            return (((string, level), sorted(element for element in input_strings if element.startswith(string))) for string in self.all_at_level(input_strings, level))
        
    def cluster_all_levels(self, input_strings_iter):
        input_strings = list(input_strings_iter)
        return itertools.chain(self.cluster_one_level(input_strings, None), 
                               itertools.chain.from_iterable(itertools.takewhile(len, (list(self.cluster_one_level(input_strings, i)) for i in itertools.count(1))))
                               )
        
    def all_at_level(self, input_strings, level):        
        result = itertools.ifilter(None, (self.at_level(string, level) for string in input_strings))        
        return set(result) 
    
    def at_level(self, string, level):
        parts = string.split(self.__delimiter, level)
        if len(parts) >= level:
            return self.__delimiter.join(parts[:level])
        else:
            return None

    def decompose(self, string):
        return string.split(self.__delimiter)

    def limited_to(self, string, maxparts):
        return self.__delimiter.join(string.split(self.__delimiter, maxparts)[:maxparts])

class CompleteEnumerationMap(object):
# TODO das funktioniert so nicht...
    def __init__(self, enumeration, dictionaries):
        if isinstance(dictionaries, dict):
            dictionary = dictionaries
        else:
            dictionary = dict()
            for in_dict in dictionaries:
                dictionary.update(in_dict)

        enumeration.check_missing_values(dictionary)
        #object.__setattr__(self, "__dictionary", dictionary)
        #self.__dict__['__dictionary'] = dictionary
        self.__dictionary = dictionary

    def __getattr__(self, attr):
        """ Delegate access to dictionary """
        return getattr(self.__dictionary, attr)

#    def __setattr__(self, attr, value):
#        """ Delegate access to dictionary """
#        return setattr(self.__dictionary, attr, value)

class DictTools(object):
    
    @staticmethod
    def merge_dict(target_dict, other_dict, value_merge_func, key_merge_func=lambda x: x):
        """
        Merges a dictionary into another.
        
        @param target_dict: a dict 
        @param other_dict: a dict-like readable object with an iteritems() method or item iterator
        @param value_merge_func: May be None, then trying to merge dictionaries with conflicting 
            keys will raise a ValueError (?).
        @param key_merge_func: a function to transform the keys of other_dict while merging. The default 
            is not to modify the keys.
        @return: the target_dict
        
        >>> DictTools.merge_dict(dict(), ((1, 'a'), ), value_merge_func=None)
        {1: 'a'}
        >>> dict({1: 'a', 2: 'b'}) == DictTools.merge_dict(dict({2: 'b'}), ((1, 'a'), ), value_merge_func=None)
        True
        """
        try:
            other_dict_items = other_dict.iteritems()        
        except AttributeError:
            other_dict_items = other_dict
        for key, value in other_dict_items:
            merged_key = key_merge_func(key)
            if merged_key in target_dict:
                target_dict[merged_key] = value_merge_func(target_dict[merged_key], value)
            else:
                target_dict[merged_key] = value
        return target_dict

class DictReaderTools(object):
    @staticmethod
    def transform_to_set_valued_dict_sorted(inputFileReader, keyKey, valueKey):
        """
        Equivalent to transform_to_set_valued_dict if the input data is sorted by the key. 
        
        @see: L{DictReaderTools.transform_to_set_valued_dict}
        """
        return dict((key, set(dict[valueKey] for dict in dicts)) 
                    for (key, dicts) in groupby(inputFileReader, lambda dict: dict[keyKey]))

    @staticmethod
    def transform_to_set_valued_dict(inputFileReader, keyKey, valueKey):
        """
        Transform a dict-reader to a set-valued dictionary.
        
        @see: L{SetValuedDictTools} for the description of a set-valued dictionary.
        
        @param inputFileReader: an iterator of dictionaries, such as one returned by csv.DictReader
        @param keyKey: the name of the key column to use
        @param valueKey: the name of the value column
        
        @todo: allow using a list of key and value columns
        """        
        dependencies = dict()
        for row in inputFileReader:
            if row[keyKey] not in dependencies:
                dependencies.update(dict({row[keyKey]:set()}))
            dependencies[row[keyKey]].add(row[valueKey])

        return dependencies

class Deque:
    'Fast searchable queue'
    def __init__(self):
        self.od = OrderedDict()
    def appendleft(self, k):
        od = self.od
        if k in od:
            del od[k]
        od[k] = None
    def pop(self):
        return self.od.popitem(0)[0]
    def remove(self, k):
        del self.od[k]
    def __len__(self):
        return len(self.od)
    def __contains__(self, k):
        return k in self.od
    def __iter__(self):
        return reversed(self.od)
    def __repr__(self):
        return 'Deque(%r)' % (list(self),)

## {{{ http://code.activestate.com/recipes/576532/ (r1)
class AdaptiveReplacementCache(object):
    """
    >>> dec_cache = AdaptiveReplacementCache(10)
    >>> @dec_cache
    ... def identity(f):
    ...     return (f, str(f))
    >>> dummy = [identity(x) for x in range(20) + range(11,15) + range(20) +
    ... range(11,40) + [39, 38, 37, 36, 35, 34, 33, 32, 16, 17, 11, 41]] 
    >>> dec_cache.t1
    Deque([(41,)])
    >>> dec_cache.t2
    Deque([(11,), (17,), (16,), (32,), (33,), (34,), (35,), (36,), (37,)])
    >>> dec_cache.b1
    Deque([(31,), (30,)])
    >>> dec_cache.b2
    Deque([(38,), (39,), (19,), (18,), (15,), (14,), (13,), (12,)])
    >>> dec_cache.p
    5
    
    # TODO how do I invalidate an entry? dec_cache.replace(i) ?
    """
    def __init__(self, size):
        self.cached = {}
        self.c = size
        self.p = 0
        self.t1 = Deque()
        self.t2 = Deque()
        self.b1 = Deque()
        self.b2 = Deque()

    def replace(self, args):
        if self.t1 and (
            (args in self.b2 and len(self.t1) == self.p) or
            (len(self.t1) > self.p)):
            old = self.t1.pop()
            self.b1.appendleft(old)
        else:
            old = self.t2.pop()
            self.b2.appendleft(old)
        del(self.cached[old])
        
    def __call__(self, func):
        def wrapper(*orig_args):
            """decorator function wrapper"""
            args = orig_args[:]
            if args in self.t1: 
                self.t1.remove(args)
                self.t2.appendleft(args)
                return self.cached[args]
            if args in self.t2: 
                self.t2.remove(args)
                self.t2.appendleft(args)
                return self.cached[args]
            result = func(*orig_args)
            self.cached[args] = result
            if args in self.b1:
                self.p = min(
                    self.c, self.p + max(len(self.b2) / len(self.b1) , 1))
                self.replace(args)
                self.b1.remove(args)
                self.t2.appendleft(args)
                #print "%s:: t1:%s b1:%s t2:%s b2:%s p:%s" % (
                #    repr(func)[10:30], len(self.t1),len(self.b1),len(self.t2),
                #    len(self.b2), self.p)
                return result            
            if args in self.b2:
                self.p = max(0, self.p - max(len(self.b1)/len(self.b2) , 1))
                self.replace(args)
                self.b2.remove(args)
                self.t2.appendleft(args)
                #print "%s:: t1:%s b1:%s t2:%s b2:%s p:%s" % (
                #   repr(func)[10:30], len(self.t1),len(self.b1),len(self.t2),
                #   len(self.b2), self.p)
                return result
            if len(self.t1) + len(self.b1) == self.c:
                if len(self.t1) < self.c:
                    self.b1.pop()
                    self.replace(args)
                else:
                    del(self.cached[self.t1.pop()])
            else:
                total = len(self.t1) + len(self.b1) + len(
                    self.t2) + len(self.b2)
                if total >= self.c:
                    if total == (2 * self.c):
                        self.b2.pop()
                    self.replace(args)
            self.t1.appendleft(args)
            return result
        return wrapper
## end of http://code.activestate.com/recipes/576532/ }}}

class DAGTools(object):
    @staticmethod
    def dfs(initial, descent):
        """
        Performs a depth-first search through a dag-like structure. Equivalent to dfs_unique 
        if the structure is a tree. 
        
        @param initial: the starting elements
        @type initial: Iterable of some elements  
        @param descent: the function that delivers the children of an element
        @type descent: Callable that accepts an element as parameter and returns an iterable of elements
        @rtype: Iterable of elements
        """
        for cls in initial:
            for basecls in descent(cls):
                yield basecls
    
    @staticmethod
    def bfs_unique(initial, descent):
        """
        Performs a breadth-first search through a dag-like structure, returning each element only once. 
        
        @param initial: the starting elements
        @type initial: Iterable of some elements  
        @param descent: the function that delivers the children of an element
        @type descent: Callable that accepts an element as parameter and returns an iterable of elements
        @rtype: Iterable of elements (currently, a list)
        """
        # TODO use an ordered set instead of list in Py2.7/3.1
        adaptees = list(initial)
        for cls in adaptees:
            for basecls in descent(cls):
                if basecls not in adaptees:
                    adaptees.append(basecls)
        return adaptees
        
class ClassTools(object):
    @staticmethod
    def all_base_classes(classes):
        return DAGTools.bfs_unique(initial=classes, descent=lambda cls: cls.__bases__)
    
    @staticmethod
    def get_constructor(cls):
        """Return constructor for class object, or None if there isn't one."""
        try:
            return cls.__init__.im_func
        except AttributeError:
            for base in cls.__bases__:
                constructor = ClassTools.get_constructor(base)
                if constructor is not None:
                    return constructor
        return None
    
    @staticmethod
    def __get_arg_names(func):
        argspec = inspect.getargspec(func)
        
        return argspec[0][1:]
        
    @staticmethod
    def get_constructor_args(cls):
        constructor = ClassTools.get_constructor(cls)
        if constructor:
            return ClassTools.__get_arg_names(constructor)
        else:
            return ()
    
class DefaultAdaptable(Adaptable):
    @classmethod
    def get_adaptees(cls):
        return ClassTools.all_base_classes(cls.get_special_adaptees())
        
    @classmethod
    def get_special_adaptees(cls):
        return (cls,)
    
    def adapt_to(self, class_object_or_objects):
        if isinstance(self, class_object_or_objects):
            return self
        else:
            return None

def call_and_return(callee, returnee):
    """
    A helper function to wrap a side effect (callee) in an expression.
    
    @param callee: a 0-ary function
    @param returnee: a value
    
    @rtype: type of returnee
    """
    
    callee()
    return returnee

def isinstance_or_duck_dummy(obj, cls):
    return True

def isinstance_or_duck_inheritance(obj, cls):
    return isinstance(obj, cls)

def isinstance_or_duck_any(obj, cls):
    raise NotImplementedError

isinstance_or_duck = isinstance_or_duck_dummy

#doctest
if __name__ == "__main__":
    import doctest
    doctest.testmod()
