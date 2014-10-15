#! /usr/bin/env python

from distutils.core import setup

setup(
    name="qmpc",
    version="0.1.0",
    description="MPD client for the Nokia N900",
    long_description="MPD client for the Nokia N900, written in Python and Qt",
    author="Joerg Mechnich",
    #author_email="",
    url="https://github.com/jmechnich/qmpc",
    download_url="https://github.com/jmechnich/qmpc/releases",
    packages=["qmpclib"],
    data_files=[("share/qmpc/images", ["data/background.png"]),
                ("share/applications/hildon", ["data/qmpc.desktop"]),
                ("share/icons/hicolor/64x64/apps", ["data/qmpc.png"]),
            ],
    scripts=["qmpc"],
    keywords=["mpd"],
)
