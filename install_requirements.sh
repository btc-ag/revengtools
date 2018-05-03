#!/bin/bash

# pysvn
wget "http://pysvn.barrys-emacs.org/source_kits/pysvn-1.9.5.tar.gz"
tar xvzf pysvn-1.9.5.tar.gz
cd pysvn-1.9.5/Source
python setup.py configure --pycxx-dir=../Import/pycxx-7.0.3
make
PYTHON_USER_SITE_PACKAGES_DIR=$(python -m site --user-site)
mkdir ${PYTHON_USER_SITE_PACKAGES_DIR}/pysvn
cp pysvn/__init__.py ${PYTHON_USER_SITE_PACKAGES_DIR}/pysvn
cp pysvn/_pysvn*.so ${PYTHON_USER_SITE_PACKAGES_DIR}/pysvn
cd ../..

# wxPython
wget "https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-14.04/wxPython-4.0.1-cp27-cp27mu-linux_x86_64.whl"
pip install wxPython-4.0.1-cp27-cp27mu-linux_x86_64.whl

# Normal packages
pip install -r requirements.txt