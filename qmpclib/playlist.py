from PyQt4.Qt import *

import mpd, socket

class NowPlayingDelegate(QStyledItemDelegate):
    def __init__(self,parent=None):
        super(NowPlayingDelegate,self).__init__(parent)
        
    def paint(self, painter, option, index):
        option.palette.setColor(QPalette.Text, Qt.red)
        option.palette.setColor(QPalette.HighlightedText, Qt.red)
        super(NowPlayingDelegate,self).paint( painter, option, index)
        
class Playlist(QWidget):
    col = type("PlaylistColumns", (object,), dict((v,k) for k,v in enumerate(
        ["id", "artist", "title"]
    )))
    
    @staticmethod
    def columns():
        return len(dict((k,v) for k,v in Playlist.col.__dict__.items()
                        if not k.startswith("__")))

    def __init__(self,mpd,parent=None):
        super(Playlist,self).__init__(parent)
        self.mpd = mpd
        self.model = QStandardItemModel(0,self.columns(),self)
        self.initState()
        self.initGUI()
        QTimer.singleShot(100, self.adjustColumnWidth)

    def adjustColumnWidth(self):
        self.view.setColumnHidden(self.col.id,True)
        fm = QFontMetrics(self.view.font())
        total = self.view.horizontalHeader().width()
        self.view.setColumnWidth(self.col.artist, total/2)
        self.view.setColumnWidth(self.col.title,  total/2)
    
    def initState(self):
        self.timer = None
        self.song  = -1
        self.updateCounter=0
        
    def initGUI(self):
        self.setWindowTitle(QApplication.applicationName())
        layout = QVBoxLayout()

        self.view = QTableView()
        self.view.verticalHeader().hide()
        self.view.verticalHeader().setResizeMode(QHeaderView.Fixed)
        self.view.verticalHeader().setDefaultSectionSize(50)
        self.view.horizontalHeader().setStretchLastSection(True)
        self.view.horizontalHeader().hide()
        self.view.setModel(self.model)
        self.view.setSelectionMode( QAbstractItemView.SingleSelection)
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.view.doubleClicked.connect(self.doubleClicked)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.contextMenu)
        self.standardDelegate = QStyledItemDelegate(self.view)
        self.playingDelegate  = NowPlayingDelegate(self.view)
        layout.addWidget(self.view)
        self.setLayout(layout)
        
    def contextMenu(self,pos):
        if self.model.rowCount() == 0: return
        mi = self.view.indexAt(pos)
        popup = QMenu()
        actionDelete  = popup.addAction("Delete")
        actionDetails = popup.addAction("Details")
        actionClear   = popup.addAction("Clear")
        action=popup.exec_(pos)
        if action == actionDelete:
            ans = QMessageBox.question(
                self, "Remove Selected Song", "Are you sure?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ans == QMessageBox.Yes:
                try:
                    self.mpd.delete(mi.row())
                    self.model.takeRow(mi.row())
                    self.updateStatus()
                except: pass
        elif action == actionDetails:
            self.showDetails(mi)
        elif action == actionClear:
            ans = QMessageBox.question(
                self, "Clear playlist", "Are you sure?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ans == QMessageBox.Yes:
                self.mpd.clear()
                self.updateStatus()
    
    def showDetails(self,index):
        info = self.mpd.playlistid(
            self.model.item(index.row(),self.col.id).text())
        if isinstance(info,list) and len(info):
            info = self.mpd.unifySongInfo(info[0])
        d = QDialog(self)
        d.setWindowTitle("Track Details")
        layout = QGridLayout()
        layout.addWidget(QLabel("Artist:"),0,0)
        layout.addWidget(QLabel(info["artist"]),0,1)
        layout.addWidget(QLabel("Title:"),1,0)
        layout.addWidget(QLabel(info["title"]),1,1)
        layout.addWidget(QLabel("Albumartist:"),2,0)
        layout.addWidget(QLabel(info["albumartist"]),2,1)
        layout.addWidget(QLabel("Album:"),3,0)
        layout.addWidget(QLabel(info["album"]),3,1)
        layout.addWidget(QLabel("Time:"), 0, 2)
        layout.addWidget(QLabel(info["length"]), 0, 3)
        layout.addWidget(QLabel("Year:"), 1, 2)
        layout.addWidget(QLabel(info["year"]), 1, 3)
        layout.addWidget(QLabel("Track:"), 2, 2)
        layout.addWidget(QLabel(info["track"]), 2, 3)
        layout.addWidget(QLabel("ID:"), 3, 2)
        layout.addWidget(QLabel(info["id"]), 3, 3)
        d.setLayout(layout)
        d.exec_()

    def doubleClicked(self,index):
        try:
            self.mpd.play(index.row())
            self.updateStatus(False)
        except: pass
        
    def hideEvent(self, ev):
        super(Playlist,self).hideEvent(ev)
        if self.timer:
            self.killTimer( self.timer)
            self.initState()

    def showEvent(self,ev):
        super(Playlist,self).showEvent(ev)
        if not self.timer:
            self.updateStatus()
            if self.song > -1:
                QApplication.processEvents()
                curindex = self.model.index(self.song,self.col.artist)
                self.view.scrollTo(curindex)
            self.timer = self.startTimer(1000)

    def timerEvent(self,ev):
        try:
            self.updateCounter = (self.updateCounter+1)%5
            self.updateStatus(self.updateCounter==0)
        except mpd.ConnectionError, e:
            self.hide()
            QMaemo5InformationBox.information(
                self, "Connection Error: %s" % str(e),
                QMaemo5InformationBox.DefaultTimeout)
        except socket.error, e:
            QMaemo5InformationBox.information(
                self, "Connection Error: %s" % e[1],
                QMaemo5InformationBox.DefaultTimeout)
            self.hide()
    
    def updateStatus(self,updatePlaylist=True):
        if updatePlaylist:
            pls = self.mpd.playlistinfo()
            pos = 0
            selected = self.view.selectionModel().currentIndex()
            prevselid = -1 if not selected.isValid() else \
                        int(self.model.item(selected.row(),self.col.id).text())
            for pos, song in enumerate(pls):
                song = self.mpd.unifySongInfo(song)
                newrow = [QStandardItem(song[s])
                          for s in ['id','artist','title']]
                if pos < self.model.rowCount():
                    oldrow = [self.model.item(pos, i)
                              for i in xrange(self.model.columnCount())]
                    for i in xrange(self.model.columnCount()):
                        if oldrow[i].text() != newrow[i].text():
                            break
                    else: continue
                    self.model.takeRow(pos)
                    self.model.insertRow(pos,newrow)
                else:
                    self.model.appendRow(newrow)
                self.view.setItemDelegateForRow(
                    pos, self.standardDelegate)

            for idx in xrange(pos+1,self.model.rowCount()):
                self.model.takeRow(idx)
            
            selectedRemoved = False if len(self.model.findItems(
                str(prevselid),Qt.MatchExactly,self.col.id)) else True
            selectPos = -1
            if selectedRemoved:
                selectPos = selected.row()
            else:
                selected = self.view.selectionModel().currentIndex()
                selid = -1 if not selected.isValid() else \
                        int(self.model.item(selected.row(),self.col.id).text())
                if prevselid != -1 and selid != -1 and prevselid != selid:
                    for pos in xrange(self.model.rowCount()):
                        id = int(self.model.item(pos,self.col.id).text())
                        if id == prevselid:
                            selectPos = pos
                            break
            if selectPos != -1:
                print "Selecting row", selectPos
                QTimer.singleShot(
                    0, lambda: self.view.setCurrentIndex(
                        self.model.index(selectPos,self.col.id)))
            
            if not len(pls) and self.model.rowCount():
                self.model.removeRows(0,self.model.rowCount())
                if self.song > -1:
                    self.view.setItemDelegateForRow(
                        self.song, self.standardDelegate)
                self.song = -1
            
        status = self.mpd.status()
        song = int(status.get('song', -1))
        if self.model.rowCount() == 0:
            if self.song > -1:
                self.view.setItemDelegateForRow(
                    self.song, self.standardDelegate)
            self.song = -1
        if song != self.song:
            for col in xrange(self.model.columnCount()):
                if self.song > -1:
                    self.view.setItemDelegateForRow(
                        self.song, self.standardDelegate)
                if song > -1:
                    self.view.setItemDelegateForRow(
                        song, self.playingDelegate)
            self.song = song

    def reset(self):
        self.hide()
        self.initState()
        if self.model.rowCount():
            self.model.removeRows(0,self.model.rowCount())
