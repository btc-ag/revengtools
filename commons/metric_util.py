'''
Contains implementations of commons.core_if.ContentMetric.

Created on 26.05.2011

@author: SIGIESEC
'''
from commons.core_if import ContentMetric

class PlainLinesOfCodeMetric(ContentMetric):   
    def apply_metric(self, lines):
        i = -1
        for i, _l in enumerate(lines):
            pass
        return i + 1
