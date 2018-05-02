#Prepare Python env and add site-packages
import sys
import os
import subprocess
import optparse
import time
import generate_hudson_index_page_run
import shutil
from commons.bashconfig import BashConfigParser


def main():
#Check vars
    if 'CONFIG' not in os.environ:
        print "Please set the CONFIG var!"
        sys.exit(-1)
    os.environ['REVENGTOOLS_DIST'] = os.path.dirname(generate_hudson_index_page_run.__file__)
    os.environ['XSLT_PROGRAM'] = os.path.normpath(os.path.sep.join((os.getcwd(), "/external/saxon/Transform.exe")))
    os.environ['GRAPHVIZ_BIN_DIR'] = os.path.normpath(os.path.sep.join((os.getcwd(), "/external/graphviz/bin")))
        #Create Python path if it is not existing in the System
    if 'PYTHONPATH' not in os.environ:
        os.environ['PYTHONPATH'] = ""
    os.environ['PYTHONPATH'] += ";site-packages;site-packages/python_graph_core-1.7.0-py2.6.egg;site-packages/mock-0.8.0beta4-py2.6.egg;"
    #Parse Commandline Options
    parse = optparse.OptionParser()
    parse.add_option("", "--rulesonly", action="store_true", dest="rules_only")
    options, args = parse.parse_args()
    #Parse Config
    configParser = BashConfigParser(os.path.join(os.environ["REVENGTOOLS_DIST"], "configuration", os.environ['CONFIG']))
    lang = configParser.get("LANGUAGE")
    result_dir = configParser.get("RESULTS_DIR")
    print ">> Language: " + lang
    print ">> Results dir: " + result_dir
    try:
        os.remove(os.path.join(result_dir, "generated_graphs.csv"))
    except WindowsError:
        print "INFO: Could not delete file %s" % os.path.join(result_dir, "generated_graphs.csv")
    if not os.path.isdir(result_dir):
        os.system("mkdir %s" % os.path.join(result_dir))
        print "mkdir %s" % os.path.join(result_dir)
    script_fullname = os.path.join(os.environ["REVENGTOOLS_DIST"], "parse_link_dependencies_generic_run.py")
    if lang == "cpp":
        raise NotImplementedError
    elif not options.rules_only:
        runPythonSkript(["parse_link_dependencies_generic_run.py", "-l"])
        #TODO: Er macht im ersten Schritt mehr als in process_link_deps, da er auch ifonly macht
        #      und nicht nur focused_module
        #runPythonSkript(["parse_link_dependencies_generic_run.py","-l","--focus_on_each_group"])
        # TODO das ist so sehr umstaendlich (von sigiesec)
        runPythonSkript([script_fullname], {"SECTION_PREFIX":"ifonly", "FLAVOR":"ifonly"})
        runPythonSkript([script_fullname], {"SECTION_PREFIX":"wraponly", "FLAVOR":"wraponly"})
        runPythonSkript([script_fullname], {"SECTION_PREFIX":"toplevel", "FLAVOR":"toplevel"})
        runPythonSkript([script_fullname])
    else:
        runPythonSkript([script_fullname, "--no_graphs", "-l"])
    generate_hudson_index_page_run.main()
    configurationPath = os.path.sep.join((configParser.get("REVENGTOOLS_DIST"), "configuration", "hudson", ""))
    #Copying configurationPath and its direct subdirs to results_dir and ignoring hidden directories and files
    #TODO: There should be a function in shutil but neither shutil.copytree or distutils.dir_util.copy_tree work
    #      shutil.copytree does not allow the directory to exist and
    #      distutils.dir_util.copy_tree does not have a ignore case
    #      and also the following code copies the svn directory:
    #      os.system("cp -r %s/configuration/hudson/* %s"%(configParser.get("REVENGTOOLS_DIST"),configParser.get("RESULTS_DIR")))
    src_files = os.listdir(configurationPath)
    for file_name in src_files:
        full_file_name = os.path.join(configurationPath, file_name)
        if (os.path.isfile(full_file_name)) and not file_name.startswith("."):
            result_file = os.path.join(result_dir, file_name)
            print "copy %s to %s" % (full_file_name, result_file)
            shutil.copy(full_file_name, result_dir)
        if (os.path.isdir(full_file_name)) and not file_name.startswith("."):
            src_files_in_subdir = os.listdir(full_file_name)
            for file_name_in_dir in src_files_in_subdir:
                full_file_name_in_dir = os.path.join(full_file_name, file_name_in_dir)
                if (os.path.isfile(full_file_name_in_dir)) and not full_file_name.startswith("."):
                    if not os.path.isdir(os.path.join(result_dir, file_name)):
                        os.system("mkdir %s" % os.path.join(result_dir, file_name))
                        print "mkdir %s" % os.path.join(result_dir, file_name)
                    result_file = os.path.join(result_dir, file_name, file_name_in_dir)
                    print "copy %s to %s" % (full_file_name_in_dir, result_file)
                    shutil.copy(full_file_name_in_dir, result_file)

def runPythonSkript(command, env = None):
    #Setup Enviroment
    if env is not None:
        for key in env:
            os.environ[key] = env[key]
    
    #Inform the user what we are doing
    # TODO do not output this on stdout but on stderr
    print ">> Running Skript '{0}' with env={1}".format(" ".join(command), env)
    
    #Prepare and execute the subprocess
    #Path to python interpreter
    call = ['python'] 
    call.extend(command)
    start_time = time.time()
    subprocess.check_call(call)
    end_time = time.time()
    print ">> Finished ({0} secs)".format(end_time - start_time) 
    
    #Teardown Enviroment
    if env is not None:
        for key in env:
            del os.environ[key]
            
if __name__ == "__main__":    
    main()
