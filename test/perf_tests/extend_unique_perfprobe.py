'''
Created on 03.01.2012

@author: SIGIESEC
'''

from timeit import Timer
import platform

KEY_COLUMN="key_column"
VALUE_COLUMN="value_column"

def generate_input_data(length):
    for i in range(length):
        yield i

def measure(func, iterations, count):
    time = Timer(func + "([], input_data)", 
                 setup="""from commons.core_util import CollectionTools; from __main__ import generate_input_data, KEY_COLUMN, VALUE_COLUMN; input_data = list(generate_input_data(length=%i))""" % (count, )).repeat(repeat=3, number=iterations)
    print "%s,%i,%s" % (func, count, ",".join(map(str, time)))    

if __name__ == "__main__":
    print "Python version %s (%s)" % (platform.python_version(), getattr(platform, "python_implementation", lambda: "Unknown")())
    print platform.platform()
    for count in range(0, 100, 5):
        measure("CollectionTools.extend_unique", count=count, iterations=1000)
        #measure("CollectionTools.extend_unique_slow", count=count, iterations=1000)
        measure("extend", count=count, iterations=1000)
