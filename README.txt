PREREQUISITES for using the RevEngTools

For the shell script-based tools:

GNU bash, coreutils, sed, grep, diffutils (tested with cygwin unter Windows XP SP2 and Windows Server 2003 64-Bit)
SQL Server 2005 sqlcmd client

For the python-based tools:

Python 2.6 (tested with 2.6.5)
pyparsing (tested with 1.5.2)
pydot (tested with 1.0.2)

*******************************************************************************
Tutorial for Running the UnitTests
*******************************************************************************
- install pygraph 
   (on 64bit Win: - download zip from http://code.google.com/p/python-graph/downloads/list
                  - unpack
                  - run python setup -install in pythongraph/core)
                  
- install mock (- http://pypi.python.org/pypi/mock#downloads
                - unpack
                - run python setup install in mock...)
                
*******************************************************************************
How to Get the Instances for a Concrete Configuration
*******************************************************************************
One possibility is to take a look in the autowire files for
LANGUAGE, VERSION, SYSTEM=CABNET-HUDSON-OLGA0822 and the default autowire.

Another possibility is to use a shell with grep <String> File
                              f.e. grep "ModuleLinkDepsSupply" autowire.config*

Now possible is: $ CONFIG=config.CABNET-CHRISTIAN-LOKAL python –m commons/configurator_dump_run
