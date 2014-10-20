from PyQt4.QtCore import Qt
from PyQt4.QtGui  import QWidget, QApplication, QFontMetrics, QFont, \
    QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QSlider, QMenu, \
    QToolButton, QStackedWidget, QIcon

from mpd import ConnectionError
import socket

class Player(QWidget):
    def __init__(self,app):
        super(Player,self).__init__()
        self.mpd   = app.mpd
        self.ih    = app.imagehelper
        self.timer = None
        self.initGUI()
        self.initState()
        
    def initGUI(self):
        self.setWindowTitle(QApplication.applicationName())
        self.fmt = QFontMetrics(QFont())
        layout = QVBoxLayout()
        
        toplayout = QHBoxLayout()
        currentLayout = QGridLayout()
        currentLayout.setContentsMargins(0,20,0,20)
        currentLayout.setHorizontalSpacing(100)
        currentLayout.setVerticalSpacing(20)
        # current song information
        currentLayout.addWidget(QLabel("<b>Artist</b>"),1,0)
        self.artist = QLabel()
        currentLayout.addWidget(self.artist,1,1)
        currentLayout.addWidget(QLabel("<b>Title</b>"),2,0)
        self.title  = QLabel()
        currentLayout.addWidget(self.title,2,1)
        currentLayout.addWidget(QLabel("<b>Albumartist</b>"),3,0)
        self.albumartist = QLabel()
        currentLayout.addWidget(self.albumartist,3,1)
        currentLayout.addWidget(QLabel("<b>Album</b>"),4,0)
        self.album  = QLabel()
        currentLayout.addWidget(self.album,4,1)
        # playlist and song position
        self.playlistposition = QLabel()
        currentLayout.addWidget(self.playlistposition,5,0)
        poslayout = QHBoxLayout()
        poslayout.setSpacing(10)
        self.time = QLabel("00:00")
        poslayout.addWidget(self.time)
        self.position = QSlider(Qt.Horizontal)
        self.position.setTracking(False)
        self.position.setSingleStep(10)
        self.position.sliderReleased.connect( self.seek)
        self.position.sliderMoved.connect(
            lambda x: self.time.setText(self.mpd.timeString(x)))
        poslayout.addWidget(self.position)
        self.length = QLabel("00:00")
        poslayout.addWidget(self.length)
        currentLayout.addLayout(poslayout,5,1)
        toplayout.addLayout(currentLayout)
        layout.addLayout(toplayout)
        layout.addStretch(1)
        
        self.settingsWidget = QMenu()
        self.consumeBtn = self.settingsWidget.addAction("Consume")
        self.consumeBtn.setCheckable(True)
        self.consumeBtn.triggered.connect( lambda x: self.mpd.consume(int(x)))
        self.singleBtn  = self.settingsWidget.addAction("Single")
        self.singleBtn.setCheckable(True)
        self.singleBtn.triggered.connect( lambda x: self.mpd.single(int(x)))
        
        toolLayout = QHBoxLayout()
        self.settingsBtn = QToolButton()
        self.settingsBtn.setFixedSize(64,64)
        self.settingsBtn.setIcon( self.ih.settingsButton)
        self.settingsBtn.clicked.connect(self.showAdditionalControls)
        toolLayout.addWidget(self.settingsBtn)

        
        toolWidget = QStackedWidget()
        transpWidget = QWidget()
        transpLayout = QHBoxLayout()
        self.prevBtn = self.createButton(
            self.ih.prevButton, self.ih.prevButtonPressed)
        self.prevBtn.clicked.connect( lambda x: self.mpd.previous())
        transpLayout.addWidget(self.prevBtn)
        self.playBtn = self.createCheckButton(
            self.ih.playButton, self.ih.pauseButton)
        self.playBtn.clicked.connect( self.playPressed)
        transpLayout.addWidget(self.playBtn)
        self.stopBtn = self.createButton(
            self.ih.stopButton, self.ih.stopButtonPressed)
        self.stopBtn.clicked.connect( lambda x: self.mpd.stop())
        transpLayout.addWidget(self.stopBtn)
        self.nextBtn = self.createButton(
            self.ih.nextButton, self.ih.nextButtonPressed)
        self.nextBtn.clicked.connect( lambda x: self.mpd.next())
        transpLayout.addWidget(self.nextBtn)
        self.shuffleBtn = self.createCheckButton(
            self.ih.shuffleButton, self.ih.shuffleButtonPressed)
        self.shuffleBtn.toggled.connect(
            lambda x: self.mpd.random(1) if x else self.mpd.random(0))
        transpLayout.addWidget(self.shuffleBtn)
        self.repeatBtn = self.createCheckButton(
            self.ih.repeatButton, self.ih.repeatButtonPressed)
        self.repeatBtn.toggled.connect(
            lambda x: self.mpd.repeat(1) if x else self.mpd.repeat(0))
        transpLayout.addWidget(self.repeatBtn)
        transpLayout.addSpacing(64)
        transpWidget.setLayout(transpLayout)
        toolWidget.addWidget( transpWidget)
        
        self.volume = QSlider(Qt.Horizontal)
        self.volume.valueChanged.connect(self.mpd.setvol)
        toolWidget.addWidget(self.volume)
        
        toolLayout.addWidget(toolWidget)
        self.volumeBtn = QToolButton()
        self.volumeBtn.setFixedSize(64,64)
        self.volumeBtn.setCheckable(True)
        self.volumeBtn.setIcon( self.ih.volumeButton)
        self.volumeBtn.toggled.connect(
            lambda x: toolWidget.setCurrentIndex(x))
        toolLayout.addWidget(self.volumeBtn)
        layout.addLayout(toolLayout)
        self.setLayout(layout)

    def showAdditionalControls(self):
        pos = self.settingsBtn.pos()
        pos.setY( pos.y()-self.settingsWidget.sizeHint().height())
        self.settingsWidget.popup( self.mapToGlobal(pos))

    def createCheckButton(self, offIcon, onIcon):
        i = QIcon()
        i.addPixmap( offIcon.pixmap(64), QIcon.Normal, QIcon.Off)
        i.addPixmap(  onIcon.pixmap(64), QIcon.Normal, QIcon.On)
        b = QToolButton()
        b.setFixedSize(64,64)
        b.setCheckable(True)
        b.setIcon(i)
        b.setStyleSheet("* { background: transparent }")
        return b

    def createButton(self, normal, pressed):
        b = QToolButton()
        b.setFixedSize(64,64)
        b.setIcon(normal)
        b.setStyleSheet("* { background: transparent }")
        b.pressed.connect( lambda: b.setIcon(pressed))
        b.released.connect( lambda: b.setIcon(normal))
        return b
    
    def playPressed(self,state):
        if   self.state == 'stop': self.mpd.play()
        else: self.mpd.pause(int(not state))
        
    def initState(self):
        self.songid  = -1
        self.state = 'stop'
        self.artist.setText("Unknown Artist")
        self.title.setText("Unknown Title")
        self.albumartist.setText("Unknown Artist")
        self.album.setText("Unknown Album")
        self.position.setRange(0,0)
        self.position.setValue(0)
        self.position.setEnabled(False)
        self.length.setText("00:00")
        self.playlistposition.setText("0/0")
        self.setStopState()
        
    def setStopState(self):
        self.playBtn.setChecked(False)
        self.time.setText("00:00")
        self.position.setValue(0)
        self.volume.setEnabled(False)

    def updateStatus(self):
        status = self.mpd.status()
        self.repeatBtn.setChecked(int(status['repeat']))
        self.shuffleBtn.setChecked(int(status['random']))
        self.consumeBtn.setChecked(int(status['consume']))
        self.singleBtn.setChecked(int(status['single']))
        if not status.has_key('songid') and self.songid != -1:
            self.initState()
            return
        stateChanged = False
        state = status['state']
        if state != self.state:
            stateChanged = True
        self.state = state
        volume = int(status['volume'])
        if self.state == 'play' or self.state == 'pause':
            self.playBtn.setChecked(True if self.state == 'play' else False)
            songid = int(status['songid'])
            if songid != self.songid:
                self.songid = songid
                self.updateCurrentSong()
            playlistlength = int(status['playlistlength'])
            song = int(status.get('song',-1))
            self.playlistposition.setText("%d/%d" % (song+1,playlistlength))
            playlistlength = int(status['playlistlength'])
            elapsed = float(status['elapsed'])
            if not self.position.isSliderDown():
                timeString = self.mpd.timeString(round(elapsed))
                self.time.setFixedSize(
                    (len(timeString)+1)*self.fmt.averageCharWidth(),
                    self.fmt.height())
                self.time.setText(timeString)
                if self.position.maximum() > 0:
                    self.position.setSliderPosition(round(elapsed))
            if stateChanged:
                self.volume.setEnabled(True)
            if not self.volume.isSliderDown():
                self.volume.setValue(volume)
            #nextsong = int(status['nextsong'])
        else:
            if self.songid == -1: return
            self.setStopState()
            
    def updateCurrentSong(self):
        currentsong = self.mpd.unifySongInfo(self.mpd.currentsong())
        self.artist.setText(      currentsong['artist'])
        self.title.setText(       currentsong['title'])
        self.albumartist.setText( currentsong['albumartist'])
        self.album.setText(       currentsong['album'])
        self.length.setText(      currentsong['length'])
        self.position.setRange(0,currentsong['time'])
        self.position.setEnabled(True if self.position.maximum() > 0 else False)
        self.position.setValue(0)
        self.time.setText("00:00")
        self.volume.setEnabled(True)

    def seek(self):
        secs = self.position.sliderPosition()
        if self.songid == -1: return
        self.mpd.seekid(self.songid, secs)
       
    def hideEvent(self, ev):
        if self.timer:
            self.killTimer( self.timer)
            self.timer = None
        super(Player,self).hideEvent(ev)

    def showEvent(self,ev):
        if not self.timer:
            self.updateStatus()
            self.timer = self.startTimer(1000)
        super(Player,self).showEvent(ev)

    def timerEvent(self,ev):
        try:
            self.updateStatus()
        except ConnectionError, e:
            self.hide()
            QMaemo5InformationBox.information(
                self, "Connection Error: %s" % str(e),
                QMaemo5InformationBox.DefaultTimeout)
        except socket.error, e:
            QMaemo5InformationBox.information(
                self, "Connection Error: %s" % e[1],
                QMaemo5InformationBox.DefaultTimeout)
            self.hide()
                
    def reset(self):
        self.hide()
