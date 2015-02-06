from PyQt4.QtCore import Qt, QObject, QTimer
from PyQt4.QtGui  import QMenuBar, QMainWindow, QStackedWidget, QAction, \
    QApplication, QDialog, QGridLayout, QLabel

from startscreen   import StartScreen
from player        import Player
from browser       import Browser
from playlist      import Playlist
from mpdwrapper    import MPDWrapper
from preferences   import Prefs
from imagehelper   import ImageHelper
from util          import DataModel
from platformhelper import have_maemo

if have_maemo:
    from widgets_maemo   import InformationBox
else:
    from widgets_default import InformationBox

import socket

class QMPCApp(QObject):
    __images__ = {
        'background':           "images/background.png",
    }
    
    __icons__  = {
        'homeButton':           "general_backspace",
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
        self.mw = None
        self.initData()
        self.initMPD()
        self.initActions()
        self.initGUI()
        QTimer.singleShot(100,self.deferredStart)

    def deferredStart(self):
        if self.data.autoconnect: self.connectMPD()

    def initData(self):
        self.selectedServerName = None
        self.data = DataModel()
        self.data.loadSettings()
        self.imagehelper = ImageHelper(images=self.__images__,
                                       icons=self.__icons__)
        QApplication.instance().aboutToQuit.connect(self.data.saveSettings)

    def initActions(self):
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
        self.actionPrefs = QAction("Preferences",self)
        self.actionPrefs.triggered.connect(self.showPrefs)
        self.actionConnect = QAction("Connect",self)
        self.actionConnect.triggered.connect(self.connectActivated)

    def initGUI(self):
        self.initStartScreen()
        self.initWidgets()
        
        if not have_maemo:
            self.mw     = QMainWindow()
            menu        = self.mw.menuBar()
            menufile    = menu.addMenu("&File")
            menuwindows = menu.addMenu("&Windows")
            self.mw.statusBar()
            menuwindows.addAction(self.actionPlayer)
            menuwindows.addAction(self.actionPlaylist)
            menuwindows.addAction(self.actionBrowser)
            menuwindows.addAction(self.actionStats)
            menufile.addAction(self.actionConnect)
            menufile.addAction(self.actionPrefs)
            menufile.addSeparator()
            menufile.addAction("&Quit", QApplication.quit)
       
        self.setConnectionState(False)

    def initStartScreen(self):
        self.startscreen = StartScreen(self)
        self.startscreen.clicked.connect(self.connectActivated)
        if have_maemo:
            menu = QMenuBar(self.startscreen)
            menu.addAction(self.actionConnect)
            menu.addAction(self.actionPrefs)
            
    def initWidgets(self):
        # create subwidgets
        self.player   = Player(self)
        self.playlist = Playlist(self)
        self.browser  = Browser(self)
        if have_maemo:
            # build Maemo stack hierarchy
            self.playlist.setParent(self.player)
            self.browser.setParent(self.player)
            for w in [ self.player, self.playlist, self.browser ]:
                w.setAttribute( Qt.WA_Maemo5StackedWindow)
                w.setWindowFlags( w.windowFlags() | Qt.Window)

            # add menu bar
            menu = QMenuBar(self.player)
            menu.addAction(self.actionPlaylist)
            menu.addAction(self.actionBrowser)
            menu.addAction(self.actionStats)
            menu.addAction(self.actionPrefs)
            menu.addAction(self.actionConnect)
        else:
            self.stack = QStackedWidget()
            for w in [ self.player, self.playlist, self.browser ]:
                w.setParent(self.stack)
                self.stack.addWidget(w)

    def switchView(self, connected):
        if have_maemo:
            if connected:
                self.player.show()
                self.startscreen.hide()
            else:
                self.startscreen.show()
        else:
            cw = self.mw.centralWidget()
            if cw:
                cw.setParent(None)
                cw.hide()
            if connected:
                self.mw.setCentralWidget(self.stack)
                self.stack.show()
                self.showWidget(self.player)
            else:
                self.mw.setCentralWidget(self.startscreen)
                self.startscreen.show()
            self.mw.show()

    def showWidget(self,widget):
        if not have_maemo:
            self.stack.setCurrentWidget(widget)
        widget.show()

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
            InformationBox.information( self.mw, "Select server to connect")
            self.showPrefs()

        selected = self.data.selectedServer()
        if len(selected):
            name, address, port = selected
            try:
                if not reconnect:
                    InformationBox.information(
                        self.mw, "Connecting to <b>%s</b>" % name)
                    QApplication.processEvents()
                self.mpd.timeout = 10
                self.mpd.connect( str(address), int(port))
                if not reconnect:
                    InformationBox.information(
                        self.mw, "Connected to <b>%s</b>" % name)
                    QApplication.processEvents()
                    self.setConnectionState(True)
                    self.selectedServerName = name
                self.mpdtimer = self.startTimer(5000)
            except socket.timeout, e:
                self.setConnectionState(False)
                InformationBox.information( self.mw, "%s: %s" %(name,e))
                QApplication.processEvents()
            except socket.gaierror, e:
                self.setConnectionState(False)
                InformationBox.information( self.mw, "%s: %s" %(name,e[1]))
                QApplication.processEvents()
            except socket.error, e:
                self.setConnectionState(False)
                InformationBox.information( self.mw, "%s: %s" %(name,e[1]))
                QApplication.processEvents()

    def disconnectMPD(self, reconnect=False):
        self.killTimer(self.mpdtimer)
        if not reconnect:
            message = "Disconnected"
            if self.selectedServerName:
                message += (" from <b>%s</b>" % self.selectedServerName)
            self.selectedName = None
            self.setConnectionState(False)
            InformationBox.information(self.mw, message)
            QApplication.processEvents()
            self.player.reset()
            self.browser.reset()
            self.playlist.reset()
        self.mpd.disconnect()
        
    def showStats(self):
        try:
            stats = self.mpd.stats()
        except:
            return
        d = QDialog(self.mw)
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

    def setConnectionState(self,state):
        self.actionPlayer.setEnabled(state)
        self.actionPlaylist.setEnabled(state)
        self.actionBrowser.setEnabled(state)
        self.actionStats.setEnabled(state)
        self.startscreen.updateLabel(state)
        if state:
            selected = self.data.selectedServer()
            if not len(selected): return
            self.actionConnect.setText("Disconnect")
            self.switchView(True)
            self.showWidget(self.player)
        else:
            self.actionConnect.setText("Connect")
            self.switchView(False)
            
    def showPrefs(self):
        s = Prefs(self.data, self.mw)
        s.exec_()

    def timerEvent(self,e):
        try:
            self.mpd.ping()
        except:
            self.disconnectMPD(True)
            self.connectMPD(True)

