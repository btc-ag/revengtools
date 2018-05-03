import unittest
import os
import os.path
from infrastructure.ctags.ctags_class_mapper import CTagClassMapper, MapperError, CTagLanguage
             
class CTagClassMapperTest(unittest.TestCase):
    def get_ctags_exe(self):
        # TODO this is probably neither the right place to do this, nor the right way
        if os.path.isfile("/usr/bin/ctags"):
            return "/usr/bin/ctags"
        return os.path.join(self.basedir, "../../../../external/ctags/ctags.exe")

    def setUp(self):
        #Not sure if the path change is necessary...
        self.basedir = os.path.dirname(__file__)
        self.mapper = CTagClassMapper(self.get_ctags_exe(), CTagLanguage.CSharp)
        fileList = ["TestClass1.cs","TestClass2.cs","TestClassParameter.cs"]
        fileList = [os.path.join(self.basedir,fName) for fName in fileList]
        self.mapper.create_index(fileList)
    def test_simple(self):
        self.assertEqual([os.path.join(self.basedir,"TestClass1.cs")], self.mapper.lookup_class("BTC.Test.TestClass1"))
        self.assertEqual([os.path.join(self.basedir,"TestClass1.cs")], self.mapper.lookup_class("BTC.Test.TestClass1_1"))
        self.assertEqual([os.path.join(self.basedir,"TestClass2.cs")], self.mapper.lookup_class("BTC.Test.TestClass2"))
    def test_parameterized(self):
        self.assertEqual([os.path.join(self.basedir,"TestClassParameter.cs")], self.mapper.lookup_class("BTC.Test.TestClassParameter`2"))
    def test_duplicate_types(self):
        self.mapper.create_index([os.path.join(self.basedir,"duplicateTestClass1.cs")])
        res = self.mapper.lookup_class("BTC.Test.TestClass1")
        self.assertEqual([os.path.join(self.basedir,"TestClass1.cs"),os.path.join(self.basedir,"duplicateTestClass1.cs")], res)
        
if __name__ == "__main__":
    unittest.main()
