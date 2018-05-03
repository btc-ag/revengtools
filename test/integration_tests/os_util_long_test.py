'''
Created on 12.02.2012

@author: SIGIESEC
'''
from commons.metric_util import PlainLinesOfCodeMetric
from commons.os_util import (CachingResourceMetricProcessor, 
    ResolvingResourceMetricProcessor, NullPathResolver, FileResource)
from tempfile import NamedTemporaryFile
from test.unit_tests.commons.os_util_test import AbsoluteFileLengthCalculatorTest
import os
import time
import unittest

class PlainFileLengthCalculatorImplTest(AbsoluteFileLengthCalculatorTest, unittest.TestCase):
    def create_testee(self):
        return ResolvingResourceMetricProcessor(resource_resolver=NullPathResolver(), metric=PlainLinesOfCodeMetric())

class CachingFileLengthCalculatorDecoratorTest(AbsoluteFileLengthCalculatorTest, unittest.TestCase):
    def create_testee(self):
        return CachingResourceMetricProcessor(decoratee=ResolvingResourceMetricProcessor(resource_resolver=NullPathResolver(), metric=PlainLinesOfCodeMetric()))
    
    def test_cache(self):
        f = NamedTemporaryFile(delete=False)
        f.close()
        self.assertEquals(0, self._testee.apply_metric_to_resource(FileResource(f.name)))
        self.assertFalse(self._testee.modified(FileResource(f.name)))
        time.sleep(self.get_mtime_minwait())
        with open(f.name, "wt") as f2:
            f2.write("\n")
            f2.close()
        self.assertTrue(self._testee.modified(FileResource(f.name)))
        os.unlink(f.name)
        
