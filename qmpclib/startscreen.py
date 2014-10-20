from PyQt4.QtCore import Qt
from PyQt4.QtGui  import QWidget, QVBoxLayout, QApplication, QPalette, QBrush
from qmpclib.util import ClickableLabel

class StartScreen(QWidget):
    def __init__(self, app):
        super(QWidget,self).__init__()
        self.app = app
        self.initGUI()

    def sizeHint(self):
        return self.app.imagehelper.background.size()
    
    def initGUI(self):
        self.setWindowTitle(QApplication.applicationName())
        
        # set background image
        p = self.palette()
        p.setBrush(QPalette.Background, QBrush(self.app.imagehelper.background))
        self.setPalette(p)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,50)
        layout.addStretch(1)
        self.connectButton = ClickableLabel()
        self.connectButton.setMinimumWidth( 300)
        self.connectButton.clicked.connect(self.app.connectActivated)
        self.app.connectionStatusChanged.connect(self.updateConnectButton)
        self.updateConnectButton(False)
        layout.addWidget( self.connectButton, 0, Qt.AlignCenter)
        self.setLayout(layout)
        
    def updateConnectButton(self,state):
        if state:
            selected = self.app.data.selectedServer()
            self.connectButton.setText("Connected to <b>%s</b>" %
                                       selected[0])
        else:
            self.connectButton.setText("Press <b>HERE</b> to connect")
