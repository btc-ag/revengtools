'''
Created on 06.11.2010

@author: SIGIESEC
'''
from commons.thread_util import UnTeeWorkerBase, UnTeeHelper
import logging
import sys

class UnTeeWorkerTest(UnTeeWorkerBase):
    def _do_task(self, filename):
        in_file = open(filename, "rb")
        for line in in_file:
            self._write(line)
        in_file.close()

def main():
    logging.basicConfig(level=logging.DEBUG)
    (tp, untee) = UnTeeHelper.setup_untee(40, UnTeeWorkerTest, sys.stdout)
    for name in sys.argv[1:]:
        tp.add_task(filename=name)
    tp.shutdown()
    untee.join()
    

if __name__ == '__main__':
    main()
