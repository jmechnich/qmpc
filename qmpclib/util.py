from PyQt4.Qt     import pyqtSignal
from PyQt4.QtCore import Qt, QSettings
from PyQt4.QtGui  import QLabel, QFrame, QStandardItem, QStandardItemModel

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    
    def __init__(self, text="", parent=None):
        super(ClickableLabel,self).__init__(text,parent)
        self.setFrameStyle(QFrame.Panel | QFrame.Raised);
        self.setLineWidth(2);
        self.setAlignment(Qt.AlignCenter)

    def mousePressEvent(self,ev):
        self.clicked.emit()

class DataModel(object):
    def __init__(self):
        super(DataModel,self).__init__()
        self.servers     = QStandardItemModel(0,3)
        self.selected    = ''
        self.autoconnect = False
        
    def loadSettings(self):
        settings = QSettings()
        servers = settings.value("servers", None)
        self.servers.clear()
        if servers:
            for s in servers:
                self.servers.appendRow([QStandardItem(str(i)) for i in s])
        self.selected    = str(settings.value("selected", self.selected))
        self.autoconnect = bool(settings.value("autoconnect", self.autoconnect))
        
    def saveSettings(self):
        settings = QSettings()
        servers = []
        if self.servers:
            for row in xrange(self.servers.rowCount()):
                entry = []
                for col in xrange(self.servers.columnCount()):
                    entry += [self.servers.item(row,col).text()]
                servers += [entry]
        if len(servers):
            settings.setValue("servers", servers)
        else:
            settings.setValue("servers", None)
        settings.setValue("selected", str(self.selected))
        settings.setValue("autoconnect", bool(self.autoconnect))

    def selectedServer(self):
        selectedServer = []
        if self.selected:
            result = self.servers.findItems( self.selected)
            if len(result):
                mi = result[0]
                row = mi.row()
                for col in xrange(self.servers.columnCount()):
                    selectedServer += [self.servers.item(row,col).text()]
        return selectedServer

