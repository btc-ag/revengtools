'''
Created on 06.11.2010

@author: SIGIESEC
'''
from commons.thread_util import UnTee 
import sys

def main():
    untee = UnTee([open(name, "rb") for name in sys.argv[1:]], sys.stdout)

if __name__ == '__main__':
    main()
