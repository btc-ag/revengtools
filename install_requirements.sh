#!/bin/bash

if [ "$DIST" == "" ] ; then DIST=ubuntu-14.04 ; fi
if [ "$TRAVIS" == "true" ] ; then
    INSTALL_USER=""
    PYTHON_SITE_PACKAGES_DIR=$(python -c "import sys;print sys.path[len(sys.path) - 1]")
else
    INSTALL_USER="--user"
    PYTHON_SITE_PACKAGES_DIR=$(python -m site --user-site)
fi

# pysvn
if ! python -c "import pysvn" ; then
    wget "http://pysvn.barrys-emacs.org/source_kits/pysvn-1.9.5.tar.gz"
    tar xvzf pysvn-1.9.5.tar.gz
    cd pysvn-1.9.5/Source
    python setup.py configure --pycxx-dir=../Import/pycxx-7.0.3
    make
    mkdir -p ${PYTHON_SITE_PACKAGES_DIR}/pysvn
    cp pysvn/__init__.py ${PYTHON_SITE_PACKAGES_DIR}/pysvn
    cp pysvn/_pysvn*.so ${PYTHON_SITE_PACKAGES_DIR}/pysvn
    cd ../..
    rm -rf pysvn-1.9.5 # remove for testing
fi

# wxPython
if ! python -c "import wx" ; then
    wget "https://extras.wxpython.org/wxPython4/extras/linux/gtk3/$DIST/wxPython-4.0.1-cp27-cp27mu-linux_x86_64.whl"
    pip install ${INSTALL_USER} wxPython-4.0.1-cp27-cp27mu-linux_x86_64.whl
fi

# Normal packages
pip install ${INSTALL_USER} -r requirements.txt
