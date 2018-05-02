'''
Utilities for using implementations of commons.resource_if.

Created on 14.01.2012

@author: SIGIESEC
'''
class ResourceUtil(object):
    @staticmethod
    def copy(input_resource, output_resource, buffer_size=10000):
        # TODO provide a meaningful error behaviour
        with input_resource.open(mode="r") as in_file:
            with output_resource.open(mode="w") as out_file:
                while True:
                    buf = in_file.read(buffer_size)
                    if not buf:
                        break
                    out_file.write(buf)

class LineByLineProcessor(object):
    def __init__(self, transform_func):
        self.__transform_func = transform_func
    
    def process_file(self, input_file, output_file):
        for line in input_file: 
            output_file.write(self.__transform_func(line))
            
