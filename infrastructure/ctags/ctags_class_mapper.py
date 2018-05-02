import subprocess
import collections

class MapperError(Exception):
    pass

class CTagLanguage:
    CPP = 1
    CSharp = 2

class CTagClassMapper:
    """A Interface to CTag for Classname to Filename Mapping"""
    
    languageOptionMap = {CTagLanguage.CSharp : "--c#-kinds=cis", CTagLanguage.CPP : "--c++-kinds=c"}
    
    def __init__(self, ctag_exe, language): 
        self.ctag_exe = ctag_exe
        
        #Only C# is supported at the moment
        self.language = language
        if language not in self.languageOptionMap:
            raise MapperError()
        self.index = collections.defaultdict(list)
    def _parse_ctag_line(self, line):
        res = line.split("\t")
        if len(res) == 5:
            classname = res[4].replace("namespace:","") + "." + res[0]
        else:
            classname = res[0]
        filename = res[1]
        return (classname, filename)
    def create_index(self, fileList):
        if fileList:
            ctagsPipe = subprocess.Popen([self.ctag_exe, "-f", "-", "--c#-kinds=cis"] + fileList, stdout=subprocess.PIPE)
            ctagOutput = ctagsPipe.communicate()[0]
            
            #Last line is empty => Skip parsing 
            for line in ctagOutput.split("\r\n")[:-1]:
                (classname, filename) = self._parse_ctag_line(line)
                self.index[classname].append(filename)
    def get_type_list(self):
        return dict(self.index)
    def lookup_class(self, className):
        #Strip parameter information, ctags can't handle that
        (className,_,_) = className.partition('`')
        
        if self.index.has_key(className):
            return self.index[className]
        else:
            raise MapperError()

