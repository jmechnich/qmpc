from PyQt4.QtCore import Qt
from PyQt4.QtGui  import QWidget, QStandardItemModel, QApplication, \
    QVBoxLayout, QHBoxLayout, QToolButton, QLabel, QListView, \
    QAbstractItemView, QAction, QStandardItem, QMenu, QPushButton

from mpd  import MPDError
from util import ClickableLabel

class Browser(QWidget):
    entrytype = type("EntryType", (object,), dict((v,k) for k,v in enumerate(
        ["directory", "playlist", "mediafile", "url"]
    )))
    col = type("BrowserColumns", (object,), dict((v,k) for k,v in enumerate(
        ["name", "last_modified", "entrytype", "uri"]
    )))
    
    @staticmethod
    def columns():
        return len(dict((k,v) for k,v in Browser.col.__dict__.items()
                        if not k.startswith("__")))


    def __init__(self,app):
        super(Browser,self).__init__()
        self.mpd = app.mpd
        self.ih  = app.imagehelper
        self.model = QStandardItemModel(0,self.columns(),self)
        self.initGUI()
        self.initActions()

    def initGUI(self):
        self.setWindowTitle(QApplication.applicationName())
        layout = QVBoxLayout()

        headerlayout = QHBoxLayout()
        homeBtn = QToolButton()
        homeBtn.setIcon(self.ih.homeButton)
        homeBtn.setFixedSize(64,64)
        homeBtn.clicked.connect(self.home)
        headerlayout.addWidget(homeBtn)
        label = QLabel("<b>Location</b>")
        label.setMargin(10)
        label.setFixedSize(label.sizeHint())
        headerlayout.addWidget(label)
        self.currentLocation = ClickableLabel("")
        self.currentLocation.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.currentLocation.setWordWrap(True)
        self.currentLocation.setFixedSize(400,64)
        self.currentLocation.clicked.connect(self.back)
        headerlayout.addWidget(self.currentLocation)
        headerlayout.addStretch()
        layout.addLayout(headerlayout)

        self.view = QListView()
        self.view.setSelectionMode( QAbstractItemView.SingleSelection)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.contextMenu)
        self.view.setModel(self.model)
        self.view.setModelColumn(0)
        #self.view.doubleClicked.connect(self.doubleClicked)
        self.view.activated.connect(self.activated)
        layout.addWidget(self.view)
        self.setLayout(layout)

    def initActions(self):
        self.actionAdd         = QAction("Add", self)
        self.actionAddPlay     = QAction("Add and Play", self)
        self.actionInsert      = QAction("Insert", self)
        self.actionReplace     = QAction("Replace", self)
        self.actionReplacePlay = QAction("Replace and Play", self)
        self.actionUpdate      = QAction("Update", self)
        # playlist actions
        self.actionPlsRename   = QAction("Rename", self)
        self.actionPlsDelete   = QAction("Delete", self)
            
        
    def contextMenu(self,pos):
        if self.model.rowCount() == 0: return
        mi = self.view.selectionModel().currentIndex()
        if not mi.isValid(): return
        uri = self.model.item(mi.row(),self.col.uri).text()
        entrytype = int(self.model.item(mi.row(),self.col.entrytype).text())

        addfunc = None
        if entrytype != self.entrytype.playlist:
            addfunc = self.mpd.add
        else:
            addfunc = self.mpd.load
        
        popup = QMenu()
        popup.addAction(self.actionAdd)
        popup.addAction(self.actionAddPlay)
        if entrytype == self.entrytype.mediafile or \
           entrytype == self.entrytype.url:
            popup.addAction(self.actionInsert)
        popup.addAction(self.actionReplace)
        popup.addAction(self.actionReplacePlay)
        if entrytype == self.entrytype.playlist:
            popup.addAction(self.actionPlsRename)
            popup.addAction(self.actionPlsDelete)
        else:
            popup.addAction(self.actionUpdate)
        action = popup.exec_(self.mapToGlobal(pos))
        
        status = self.mpd.status()
        if action == self.actionAdd:
            addfunc(uri)
        elif action == self.actionAddPlay:
            addfunc(uri)
            self.mpd.play(int(status['playlistlength']))
        elif action == self.actionInsert:
            song = int(status.get('song',-1))+1
            self.mpd.addid(uri,song)
        elif action == self.actionReplace:
            self.mpd.clear()
            addfunc(uri)
        elif action == self.actionReplacePlay:
            self.mpd.clear()
            addfunc(uri)
            self.mpd.play()
        elif action == self.actionUpdate:
            ans = QMessageBox.question(
                self, "Update", "Trigger update for '%s'?" % uri,
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ans == QMessageBox.Yes:
                self.mpd.update(uri)
        elif action == self.actionPlsRename:
            ans, ok = QInputDialog.getText(
                self, "Rename playlist", "Rename playlist '%s':" % uri)
            plsname = unicode(ans)
            if ok and plsname != uri:
                for pls in self.mpd.listplaylists():
                    if pls['playlist'] == plsname:
                        overwrite = QMessageBox.question(
                            self, "Rename playlist",
                            "Playlist exists, overwrite?",
                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        if overwrite == QMessageBox.Yes:
                            self.mpd.rm(plsname)
                            self.mpd.rename(uri,plsname)
                        break
                else:
                    self.mpd.rename(uri, plsname)
                    self.home()
        elif action == self.actionPlsDelete:
            ans = QMessageBox.question(
                self, "Delete '%s'" % uri, "Are you sure?" % uri,
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ans == QMessageBox.Yes:
                self.mpd.rm(uri)
                self.home()
         
    def showDirectory(self,uri):
        try:
            info = self.mpd.lsinfo(uri)
        except MPDError, e:
            print e
            return
        rows = []
        for entry in info:
            row = self.createRow(entry)
            if not row: continue
            rows += [row]
        self.currentLocation.setText(uri)
        self.updateModel(rows)
    
    def createRow(self,entry):
        row = None
        if entry.has_key('directory'):
            name = entry['directory']
            pos = name.rfind('/')
            if pos != -1: name = name[pos+1:]
            row = [name,
                   entry.get('last-modified',''),
                   str(self.entrytype.directory),
                   entry['directory']]
        elif entry.has_key('playlist'):
            name = entry['playlist']
            pos = name.rfind('/')
            if pos != -1: name = name[pos+1:]
            row = [name,
                   entry.get('last-modified',''),
                   str(self.entrytype.playlist),
                   entry['playlist']]
        elif entry.has_key('file'):
            name = ""
            if entry.has_key('artist') and entry.has_key('title'):
                name = "%s - %s" % (entry['artist'],entry['title'])
                row = [name,
                       entry.get('last-modified',''),
                       str(self.entrytype.mediafile),
                       entry['file']]
            elif entry['file'].startswith('http://'):
                row = [entry['file'],
                       '',
                       str(self.entrytype.url),
                       entry['file']]
            else:
                print 'Unknown file', entry['file']
        else:
            print 'Unknown entry', entry
        return row
        
    def updateModel(self,rows):
        self.model.clear()
        for row in rows:
            self.model.appendRow([QStandardItem(i) for i in  row])
        self.view.scrollToTop()
            
    def showEvent(self, ev):
        if self.model.rowCount() == 0:
            self.home()
        super(Browser,self).showEvent(ev)
    
    def hideEvent(self,ev):
        super(Browser,self).hideEvent(ev)

    def back(self):
        uri = unicode(self.currentLocation.text())
        pos = uri.rfind('/')
        if pos != -1:
            uri = uri[:pos]
        elif len(uri):
            uri = ''
        self.showDirectory(uri)

    def home(self):
        self.showDirectory("")

    def showPlaylist(self,uri):
        try:
            info = self.mpd.listplaylistinfo(uri)
        except MPDError, e:
            print e
            return
        rows = []
        for entry in info:
            row = self.createRow(entry)
            if not row: continue
            rows += [row]
        self.currentLocation.setText(uri)
        self.updateModel(rows)

    def activated(self,index):
        entrytype = int(self.model.item(index.row(),self.col.entrytype).text())
        if entrytype == self.entrytype.directory:
            uri = unicode(self.currentLocation.text())
            uri = '/'.join([uri, unicode(index.data())]) \
                  if len(uri) else unicode(index.data())
            self.showDirectory(uri)
        elif entrytype == self.entrytype.playlist:
            uri = self.model.item(index.row(),self.col.uri).text()
            self.showPlaylist(uri)
        elif entrytype == self.entrytype.mediafile or \
             entrytype == self.entrytype.url:
            uri = self.model.item(index.row(),self.col.uri).text()
            try:
                self.mpd.add(uri)
            except MPDError, e:
                print e
            
    def reset(self):
        self.hide()
        if self.model.rowCount() > 0:
            self.model.removeRows(0,self.model.rowCount())
