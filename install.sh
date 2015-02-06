#!/bin/sh

#PREFIX=/usr/local
PREFIX=/usr
FILES=files.txt

python setup.py build
echo "Installing to $PREFIX, keeping list of files in $FILES"
echo

sudo python setup.py install --prefix "$PREFIX" --record "$FILES"
sudo touch $PREFIX/share/icons/hicolor

echo
echo "Uninstall with 'cat $FILES | sudo xargs rm -rf'"
