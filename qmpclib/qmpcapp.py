from PyQt4.QtCore import Qt, QObject, QTimer, pyqtSignal
from PyQt4.QtGui  import QMenuBar, QMainWindow, QStackedWidget, QAction, \
    QApplication, QDialog, QGridLayout, QLabel

from qmpclib.startscreen   import StartScreen
from qmpclib.player        import Player
from qmpclib.browser       import Browser
from qmpclib.playlist      import Playlist
from qmpclib.mpdwrapper    import MPDWrapper
from qmpclib.preferences   import Prefs
from qmpclib.imagehelper   import ImageHelper
from qmpclib.util          import DataModel
from qmpclib.widgetwrapper import InformationBox

import socket

HAVE_MAEMO = False
def checkForMaemo():
    import os
    if not os.path.exists('/etc/issue'):
        return
    issue = open('/etc/issue').read().strip().lower()
    if issue.startswith('maemo'):
        global HAVE_MAEMO
        HAVE_MAEMO = True
checkForMaemo()
del checkForMaemo

class QMPCApp(QObject):
    connectionStatusChanged = pyqtSignal(bool)

    __images__ = {
        'background':           "images/background.png",
    }
    
    __icons__  = {
        'volumeButton':         "general_speaker",
        'settingsButton':       "keyboard_menu",
        'prevButton':           "/etc/hildon/theme/mediaplayer/Back.png",
        'prevButtonPressed':    "/etc/hildon/theme/mediaplayer/BackPressed.png",
        'playButton':           "/etc/hildon/theme/mediaplayer/Play.png",
        'pauseButton':          "/etc/hildon/theme/mediaplayer/Pause.png",
        'stopButton':           "/etc/hildon/theme/mediaplayer/Stop.png",
        'stopButtonPressed':    "/etc/hildon/theme/mediaplayer/StopPressed.png",
        'nextButton':           "/etc/hildon/theme/mediaplayer/Forward.png",
        'nextButtonPressed':    "/etc/hildon/theme/mediaplayer/ForwardPressed.png",
        'repeatButton':         "/etc/hildon/theme/mediaplayer/Repeat.png",
        'repeatButtonPressed':  "/etc/hildon/theme/mediaplayer/RepeatPressed.png",
        'shuffleButton':        "/etc/hildon/theme/mediaplayer/Shuffle.png",
        'shuffleButtonPressed': "/etc/hildon/theme/mediaplayer/ShufflePressed.png",
    }

    def __init__(self):
        super(QMPCApp,self).__init__()
        self.appwid = None
        self.initData()
        self.initMPD()
        self.initGUI()
        QTimer.singleShot(100,self.deferredStart)

    def deferredStart(self):
        if self.data.autoconnect: self.connectMPD()

    def initData(self):
        self.data = DataModel()
        self.data.loadSettings()
        self.imagehelper = ImageHelper(images=self.__images__,
                                       icons=self.__icons__)
        QApplication.instance().aboutToQuit.connect(self.data.saveSettings)

    def initGUI(self):
        # create subwidgets
        self.startscreen = StartScreen(self)
        self.player      = Player(self)
        self.playlist    = Playlist(self)
        self.browser     = Browser(self)

        # create actions
        self.actionPlayer = QAction("Player", self)
        self.actionPlayer.triggered.connect(
            lambda: self.showWidget(self.player))
        self.actionPlaylist = QAction("Playlist",self)
        self.actionPlaylist.triggered.connect(
            lambda: self.showWidget(self.playlist))
        self.actionBrowser = QAction("Browser",self)
        self.actionBrowser.triggered.connect(
            lambda: self.showWidget(self.browser))
        self.actionStats = QAction("Statistics",self)
        self.actionStats.triggered.connect(self.showStats)
        self.actionConnect = QAction("Connect",self)
        self.actionConnect.triggered.connect(self.connectActivated)
        
        self.menu = None
        self.menufile = None
        self.menuwindows = None
        if HAVE_MAEMO:
            self.player.setParent(self.startscreen)
            self.playlist.setParent(self.player)
            self.browser.setParent(self.player)
            for w in [ self.startscreen, self.player, self.playlist, self.browser ]:
                w.setAttribute( Qt.WA_Maemo5StackedWindow)
                w.setWindowFlags( w.windowFlags() | Qt.Window)
            self.menu = QMenuBar(self.startscreen)
            self.menufile = self.menu
            self.menuwindows = self.menu
            playerMenu = QMenuBar(self.player)
            playerMenu.addAction(self.actionPlaylist)
            playerMenu.addAction(self.actionBrowser)
            self.startscreen.show()
        else:
            mw = QMainWindow()
            self.stack = QStackedWidget()
            mw.setCentralWidget(self.stack)
            for w in [ self.startscreen, self.player, self.playlist, self.browser ]:
                w.setParent(self.stack)
                self.stack.addWidget(w)
            self.menu = mw.menuBar()
            self.menufile = self.menu.addMenu("&File")
            self.menuwindows = self.menu.addMenu("&Windows")
            mw.show()
            self.appwid = mw
       
        # create all menu bars
        self.menuwindows.addAction(self.actionPlayer)
        self.menuwindows.addAction(self.actionPlaylist)
        self.menuwindows.addAction(self.actionBrowser)
        self.menuwindows.addAction(self.actionStats)
        self.menufile.addAction(self.actionConnect)
        self.menuwindows.addAction("Preferences", self.showPrefs)
        self.setActionsEnabled(False)

        if not HAVE_MAEMO:
            self.menufile.addSeparator()
            self.menufile.addAction("&Quit", QApplication.quit)


    def showWidget(self,widget):
        if HAVE_MAEMO:
            widget.show()
        else:
            self.stack.setCurrentWidget(widget)

    def connectActivated(self):
        if self.actionConnect.text() == "Connect":
            self.connectMPD()
        else:
            self.disconnectMPD()

    def initMPD(self):
        self.mpd = MPDWrapper()
        self.mpdtimer = None
    
    def connectMPD(self,reconnect=False):
        selected = self.data.selectedServer()
        if not len(selected):
            InformationBox.information( self.appwid, "Select server to connect")
            self.showPrefs()

        selected = self.data.selectedServer()
        if len(selected):
            name, address, port = selected
            try:
                if not reconnect:
                    InformationBox.information(
                        self.appwid, "Connecting to <b>%s</b>" % name)
                    QApplication.processEvents()
                self.mpd.connect( str(address), int(port))
                if not reconnect:
                    InformationBox.information(
                        self.appwid, "Connected to <b>%s</b>" % name)
                    QApplication.processEvents()
                    self.setActionsEnabled(True)
                    self.showWidget(self.player)
                self.mpdtimer = self.startTimer(5000)
            except socket.gaierror, e:
                self.setActionsEnabled(False)
                self.showWidget(self.startscreen)
                InformationBox.information( self.appwid, "%s: %s" %(name,e[1]))
                QApplication.processEvents()
            except socket.error, e:
                self.setActionsEnabled(False)
                self.showWidget(self.startscreen)
                InformationBox.information( self.appwid, "%s: %s" %(name,e[1]))
                QApplication.processEvents()

    def disconnectMPD(self, reconnect=False):
        self.killTimer(self.mpdtimer)
        if not reconnect:
            message = "Disconnected"
            selected = self.data.selectedServer()
            if len(selected): message += (" from <b>%s</b>" % selected[0])
            InformationBox.information(self.appwid, message)
            QApplication.processEvents()
            self.setActionsEnabled(False)
            self.showWidget(self.startscreen)
            self.player.reset()
            self.browser.reset()
            self.playlist.reset()
        self.mpd.disconnect()
        
    def showStats(self):
        try:    stats = self.mpd.stats()
        except: return
        d = QDialog(self.appwid)
        d.setWindowTitle("Statistics")
        layout = QGridLayout()
        layout.addWidget(QLabel("Artists:"),0,0)
        layout.addWidget(QLabel(stats['artists']),0,1)
        layout.addWidget(QLabel("Albums:"),1,0)
        layout.addWidget(QLabel(stats['albums']),1,1)
        layout.addWidget(QLabel("Songs:"),2,0)
        layout.addWidget(QLabel(stats['songs']),2,1)
        layout.addWidget(QLabel("Uptime:"),0,2)
        layout.addWidget(QLabel(self.mpd.prettyPrintSecs(stats['uptime'])),0,3)
        layout.addWidget(QLabel("Playtime:"),1,2)
        layout.addWidget(QLabel(self.mpd.prettyPrintSecs(stats['playtime'])),1,3)
        layout.addWidget(QLabel("DB Playtime:"),2,2)
        layout.addWidget(QLabel(self.mpd.prettyPrintSecs(stats['db_playtime'])),2,3)
        d.setLayout(layout)
        d.exec_()

    def setActionsEnabled(self,state):
        self.actionPlayer.setEnabled(state)
        self.actionPlaylist.setEnabled(state)
        self.actionBrowser.setEnabled(state)
        self.actionStats.setEnabled(state)
        if state:
            selected = self.data.selectedServer()
            if not len(selected): return
            self.actionConnect.setText("Disconnect")
        else:
            self.actionConnect.setText("Connect")
        self.connectionStatusChanged.emit(state)
    
    def showPrefs(self):
        s = Prefs(self.data, self.appwid)
        s.exec_()

    def timerEvent(self,e):
        try:
            self.mpd.ping()
        except:
            self.disconnectMPD(True)
            self.connectMPD(True)

