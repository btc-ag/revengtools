'''
Created on 22.09.2010

@author: SIGIESEC
'''
from commons.os_util import NormalizedPathsIter
import csv
import sys

def main():
    delimiter = ','
    reader = NormalizedPathsIter(csv.reader(sys.stdin, delimiter=delimiter))
    for line in reader:
        print delimiter.join(line)

if __name__ == '__main__':
    main()