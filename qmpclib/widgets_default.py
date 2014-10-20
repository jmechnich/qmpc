from PyQt4.QtCore import QObject, pyqtSignal, QTimer
from PyQt4.QtGui  import QMessageBox, QPushButton, QListView, QLabel

class ListPickSelector(QObject):
    selected = pyqtSignal(str)
    
    def __init__(self, parent):
        super(ListPickSelector,self).__init__()
        self._model = None
        self._view  = None
        self._column = 0
        self._current = -1
            
    def setModel(self,model):
        self._model = model

    def model(self):
        return self._model

    def setView(self,view):
        self._view = view

    def view(self):
        return self._view

    def setModelColumn(self,col):
        self._column = col

    def modelColumn(self):
        return self._column
    
    def setCurrentIndex(self,idx):
        self._current = idx

    def currentIndex(self):
        return self._current
            
class ValueButton(QPushButton):
    def __init__(self, text, parent=None):
        super(ValueButton,self).__init__("", parent)
        self.selector = None
        self.btntext  = text
        self.valtext  = ''
        self.updateText()
        self.clicked.connect( self.showWidget)
        
    def setPickSelector(self, sel):
        self.selector = sel
        if not sel:
            return
        sel.selected.connect(self.setValueText)
        current = sel.currentIndex()
        if current == -1:
            return
        model = sel.model()
        if not model:
            return
        self.setValueText( model.item(current,sel.modelColumn()).text())
    
    def setText(self, text):
        self.btntext = text
        self.updateText()
        
    def setValueText(self, text):
        self.valtext = text
        self.updateText()
            
    def valueText(self):
        return self.valtext
            
    def updateText(self):
        text = self.btntext
        if len(self.valtext):
            if len(text): text+= '\n'
            text += self.valtext
        super(ValueButton,self).setText(text)
            
    def showWidget(self):
        if self.selector:
            w = self.selector.widget(self)
            w.show()

class InformationBox(object):
    statuslabel = None
    timer       = None
    
    @staticmethod
    def information(parent,message):
        if not InformationBox.statuslabel:
            InformationBox.statuslabel = QLabel()
            parent.statusBar().addWidget(InformationBox.statuslabel)
            InformationBox.timer       = QTimer(InformationBox.statuslabel)
            InformationBox.timer.setSingleShot(True)
            InformationBox.timer.timeout.connect(InformationBox.statuslabel.clear)
        InformationBox.timer.stop()
        InformationBox.statuslabel.setText( message)
        InformationBox.timer.start(2000)
