#!/bin/sh

find . -name "*~"    | xargs rm -f
find . -name "*.pyo" | xargs rm -f
find . -name "*.pyc" | xargs rm -f
