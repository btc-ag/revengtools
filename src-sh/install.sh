#!/bin/sh

source $(dirname ${BASH_SOURCE[0]})/configuration/config.lib.sh

PYTHON_SITEPACKAGES=$(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")

echo Installing Python packages to $PYTHON_DIR
install -b $REVENGTOOLS_DIST/site-packages/* $PYTHON_SITEPACKAGES
