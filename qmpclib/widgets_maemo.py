from PyQt4.QtMaemo5 import QMaemo5ValueButton
from PyQt4.QtMaemo5 import QMaemo5ListPickSelector as ListPickSelector
from PyQt4.QtMaemo5 import QMaemo5InformationBox
    
class ValueButton(QMaemo5ValueButton):
    def __init__(self,text,parent=None):
        super(ValueButton,self).__init__(text,parent)
        self.setValueLayout(QMaemo5ValueButton.ValueUnderText)
            
class InformationBox(object):
    @staticmethod
    def information(parent, message):
        return QMaemo5InformationBox.information(
            parent, message, QMaemo5InformationBox.DefaultTimeout)
