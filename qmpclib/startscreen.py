from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui  import QWidget, QVBoxLayout, QApplication, QPalette, QBrush, \
    QPainter, QLabel

class StartScreen(QWidget):
    clicked = pyqtSignal()
    
    def __init__(self, app):
        super(QWidget,self).__init__()
        self.app = app
        self.bg = app.imagehelper.background
        self.initGUI()

    def sizeHint(self):
        return self.app.imagehelper.background.size()
    
    def initGUI(self):
        self.setWindowTitle(QApplication.applicationName())
        
        # set background image
        p = self.palette()
        p.setBrush(QPalette.Background, QBrush(self.bg))
        self.setPalette(p)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,50)
        layout.addStretch(1)
        self.label = QLabel()
        self.updateLabel(False)
        layout.addWidget( self.label, 0, Qt.AlignCenter)
        self.setLayout(layout)
        
    def updateLabel(self,state):
        if state:
            selected = self.app.data.selectedServer()
            self.label.setText("Connected to <b>%s</b>" % selected[0])
        else:
            self.label.setText("Click to connect")

    def paintEvent(self,ev):
        p = QPainter(self)
        p.drawPixmap(0,0,self.bg)
        p.end()
    
    def mousePressEvent(self,ev):
        self.clicked.emit()
