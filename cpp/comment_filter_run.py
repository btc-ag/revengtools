'''
Created on 18.02.2012

@author: SIGIESEC
'''
from cpp.cpp_util import CommentFilter
import logging
import sys

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr,level=logging.DEBUG)
    cf = CommentFilter()
    for x in cf.filter(sys.stdin):
        print x,
