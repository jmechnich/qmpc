from PyQt4.Qt import *

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


    def __init__(self,mpd,parent=None):
        super(Browser,self).__init__(parent)
        self.mpd = mpd
        self.model = QStandardItemModel(0,self.columns(),self)
        self.initGUI()

    def initGUI(self):
        self.setWindowTitle(QApplication.applicationName())
        layout = QVBoxLayout()

        headerlayout = QHBoxLayout()
        backBtn = QToolButton()
        backBtn.setIcon(QIcon.fromTheme("general_backspace"))
        backBtn.setFixedSize(64,64)
        backBtn.clicked.connect(self.back)
        headerlayout.addWidget(backBtn)
        label = QLabel("<b>Location</b>")
        label.setMargin(10)
        label.setFixedSize(label.sizeHint())
        headerlayout.addWidget(label)
        self.currentLocation = QLabel("")
        self.currentLocation.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.currentLocation.setWordWrap(True)
        headerlayout.addWidget(self.currentLocation)
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
        
    def contextMenu(self,pos):
        if self.model.rowCount() == 0: return
        mi = self.view.selectionModel().currentIndex()
        if not mi.isValid(): return
        uri = self.model.item(mi.row(),self.col.uri).text()
        popup = QMenu()
        actionAdd         = popup.addAction("Add")
        actionAddPlay     = popup.addAction("Add and Play")
        actionInsert      = popup.addAction("Insert")
        actionReplace     = popup.addAction("Replace")
        actionReplacePlay = popup.addAction("Replace and Play")
        actionUpdate      = popup.addAction("Update")
        entrytype = int(self.model.item(mi.row(),self.col.entrytype).text())
        if not (entrytype == self.entrytype.mediafile or
                entrytype == self.entrytype.url):
            actionInsert.setEnabled(False)
        action = popup.exec_(pos)
        try:
            status = self.mpd.status()
            if action == actionAdd:
                self.mpd.add(uri)
            if action == actionAddPlay:
                self.mpd.add(uri)
                self.mpd.play(int(status['playlistlength']))
            elif action == actionInsert:
                song = int(status.get('song',-1))+1
                self.mpd.addid(uri,song)
            elif action == actionReplace:
                self.mpd.clear()
                self.mpd.add(uri)
            elif action == actionReplacePlay:
                self.mpd.clear()
                self.mpd.add(uri)
                self.mpd.play()
            elif action == actionUpdate:
                ans = QMessageBox.question(
                    self, "Update", "Trigger update for '%s'?" % uri,
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if ans == QMessageBox.Yes:
                    self.mpd.update(uri)
        except: pass
         
    def showDirectory(self):
        uri = unicode(self.currentLocation.text())
        try:    info = self.mpd.lsinfo(uri)
        except: return
        rows = []
        for entry in info:
            row = self.createRow(entry)
            if not row: continue
            rows += [row]
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
        if not len(rows): return
        self.model.clear()
        for row in rows:
            self.model.appendRow([QStandardItem(i) for i in  row])
            
    def showEvent(self, ev):
        if self.model.rowCount() == 0:
            self.currentLocation.setText("")
            self.showDirectory()
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
        self.currentLocation.setText(uri)
        self.showDirectory()

    def home(self):
        self.currentLocation.setText('')
        self.showDirectory()

    def showPlaylist(self):
        uri = unicode(self.currentLocation.text())
        try:    info = self.mpd.listplaylistinfo(uri)
        except: return
        rows = []
        for entry in info:
            row = self.createRow(entry)
            if not row: continue
            rows += [row]
        self.updateModel(rows)

    def activated(self,index):
        entrytype = int(self.model.item(index.row(),self.col.entrytype).text())
        if entrytype == self.entrytype.directory:
            uri = unicode(self.currentLocation.text())
            self.currentLocation.setText( '/'.join([uri, unicode(index.data())])
                                          if len(uri) else unicode(index.data()))
            self.showDirectory()
        elif entrytype == self.entrytype.playlist:
            uri = self.model.item(index.row(),self.col.uri).text()
            self.currentLocation.setText(uri)
            self.showPlaylist()
        elif entrytype == self.entrytype.mediafile or \
             entrytype == self.entrytype.url:
            uri = self.model.item(index.row(),self.col.uri).text()
            try:    self.mpd.add(uri)
            except: pass
            
    def reset(self):
        self.hide()
        if self.model.rowCount() > 0:
            self.model.removeRows(0,self.model.rowCount())
