qmpc
====

MPD client for the Nokia N900 smartphone, written in python and PyQt4

Functionality
=============

- Supports multiple server configurations
- Supports most basic mpd commands
- Small memory footprint (i.e. no local caching of library contents)

Requirements
============

- python-mpd2, version 0.3 (newer versions won't work with the N900's python 2.5, a fork is available from https://github.com/jmechnich/python-mpd2)
- Python 2.5
- PyQt 4.x

Installation
============

Open a terminal and execute the following commands:

```
# install dependencies
sudo gainroot
# install pyqt
apt-get install python-qt4
# install git for downloading qmpc source code
apt-get install git
exit

# download and build python-mpd2
git clone https://github.com/jmechnich/python-mpd2
(cd python-mpd2 && python setup.py build)
# download and build qmpc
git clone https://github.com/jmechnich/qmpc
(cd qmpc && python setup.py build)

# install everything
sudo gainroot
(cd python-mpd2 && python setup.py install)
(cd qmpc && ./install.sh)
exit
```

qmpc should show up in the application menu now.

Screenshots
===========

#### Start screen
![](https://raw.github.com/jmechnich/qmpc/master/screens/Screenshot-20141015-112123.png)

#### Playback window
![](https://raw.github.com/jmechnich/qmpc/master/screens/Screenshot-20141014-114538.png)

#### Playlist
![](https://raw.github.com/jmechnich/qmpc/master/screens/Screenshot-20141014-115009.png)

#### Library browser
![](https://raw.github.com/jmechnich/qmpc/master/screens/Screenshot-20141014-114407.png)
