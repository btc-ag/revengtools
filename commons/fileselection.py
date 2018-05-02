import os
import re

def find_files_with_filename_regex(basedir, regex_pattern):
    """Searches files with a given extension in basedir and all subdirs"""
    compiledPattern = re.compile(regex_pattern)
    fileList = []
    for (root, dirs, files) in os.walk(basedir):
        fileList.extend(os.path.join(root,f) for f in files if compiledPattern.match(f))
    return fileList