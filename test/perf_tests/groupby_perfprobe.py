'''
Created on 25.05.2011

@author: SIGIESEC
'''

from timeit import Timer
import platform

KEY_COLUMN="key_column"
VALUE_COLUMN="value_column"

def generate_input_data(keys, values_per_key):
    for i in range(keys):
        for j in range(values_per_key):
            yield dict({KEY_COLUMN: "key%i" % i, VALUE_COLUMN: "value%i" % j})

def measure(func, iterations):
    time = Timer(func + "(input_data, KEY_COLUMN, VALUE_COLUMN)", 
                 setup="""from commons.core_util import DictReaderTools; from __main__ import generate_input_data, KEY_COLUMN, VALUE_COLUMN; input_data = list(generate_input_data(keys=100, values_per_key=500))""").repeat(repeat=3, number=iterations)
    print "%s: %s" % (func, time)    

if __name__ == "__main__":
    print "Python version %s (%s)" % (platform.python_version(), getattr(platform, "python_implementation", lambda: "Unknown")())
    print platform.platform()
    measure("DictReaderTools.transform_to_set_valued_dict", iterations=100)
    measure("DictReaderTools.transform_to_set_valued_dict_sorted", iterations=100)
