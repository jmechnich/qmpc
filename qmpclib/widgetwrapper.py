try:
    from PyQt4.QtMaemo5 import QMaemo5ValueButton
    from PyQt4.QtMaemo5 import QMaemo5ListPickSelector as ListPickSelector
    from PyQt4.QtMaemo5 import QMaemo5InformationBox
    
    class ValueButton(QMaemo5ValueButton):
        def __init__(self,parent):
            super(ValueButton,self).__init__()
            self.setValueLayout(QMaemo5ValueButton.ValueUnderText)
            
    class InformationBox(object):
        @staticmethod
        def information(parent, message):
            return QMaemo5InformationBox(
                parent, message, QMaemo5InformationBox.DefaultTimeout)
except:
    from PyQt4.QtGui import QMessageBox, QPushButton

    # TODO: implement for other platforms (or maybe rewrite code using
    #       standard widgets)
    print "This software requires QMaemo5 libraries, exiting"
    #import sys
    #sys.exit(1)
    class ListPickSelector(object):
        def __init__(self, parent):
            super(ListPickSelector,self).__init__()
            
        def setModel(self,model):
            pass
    
        def setModelColumn(self,col):
            pass
    
        def setCurrentIndex(self,idx):
            pass
            
    class ValueButton(QPushButton):
        def __init__(self, parent):
            super(ValueButton,self).__init__()
            
        def setPickSelector(self, sel):
            pass
    
    class InformationBox(object):
        @staticmethod
        def information(parent,message):
            return QMessageBox.information(parent,"",message)
