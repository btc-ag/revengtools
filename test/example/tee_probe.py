'''
Created on 03.11.2010

@author: SIGIESEC
'''
from commons.thread_util import Tee
import sys

def main():
    tee = Tee((sys.stdout, sys.stderr))
    for i in range(1,10000):
        tee.stdin().write("Test\n")
    tee.close()

if __name__ == '__main__':
    main()
