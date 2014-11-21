#!/bin/sh

#PREFIX=/usr/local
PREFIX=/usr
FILES=files.txt

echo "Installing to $PREFIX, keeping list of files in $FILES"
echo

python setup.py install --prefix "$PREFIX" --record "$FILES"
touch $PREFIX/share/icons/hicolor

echo
echo "Uninstall with 'cat $FILES | sudo xargs rm -rf'"
