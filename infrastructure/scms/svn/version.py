# -*- coding: UTF-8 -*-

'''
Created on 13.10.2010

@author: SIGIESEC
'''
from commons.scm_if import VersionDescriber
import pysvn
import os

class SVNVersionDescriber(VersionDescriber):

    def describe_local_version(self, basepath, detailed=True):
        """
        >>> SVNVersionDescriber().describe_local_version('D:\\PRINS-Analyse\\workspace\\RevEngTools', False)
        """
        olddir = os.getcwd()
        os.chdir(basepath)
        try:
            client = pysvn.Client()
            client.exception_style = 1
            modtime = None
            if detailed:
                modified_files = client.status('.', get_all=False, ignore=True, update=True)
                revision = client.info('.').revision
                if len(modified_files) > 0:
                    modtime = max(map(lambda x: x.entry.text_time if x.entry != None else None, modified_files))
            else:
                modified_files = ()
                revision = client.info('.').revision
            if len(modified_files) > 0:
                modified_files_str = ' + [%s]' % ','.join(map(lambda x: x.path, modified_files))
            else:
                modified_files_str = ''
            os.chdir(olddir)
            return (modtime, revision.number, "SVN %i %s" % (revision.number, modified_files_str))
        except pysvn.ClientError, exc:
            raise SCMClientError("describe_local_version failed", exc)
        
        
# doctest
if __name__ == "__main__":
    import doctest
    doctest.testmod()
