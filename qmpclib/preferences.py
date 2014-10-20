from PyQt4.Qt import *

from qmpclib.widgetwrapper import *

class AddServerDialog(QDialog):
    def __init__(self,name="",address="",port=6600):
        super(AddServerDialog,self).__init__()
        self.setWindowTitle("Add Server")
        layout = QHBoxLayout()
        srvlayout = QGridLayout()
        srvlayout.addWidget(QLabel("Name"), 0, 0)
        self.name = QLineEdit(name)
        srvlayout.addWidget(self.name, 0, 1)
        srvlayout.addWidget(QLabel("Address"), 1, 0)
        self.address = QLineEdit(address)
        srvlayout.addWidget(self.address, 1, 1)
        srvlayout.addWidget(QLabel("Port"))
        self.port = QLineEdit(str(port))
        srvlayout.addWidget(self.port)
        layout.addLayout( srvlayout)
        btnbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                                  Qt.Vertical)
        btnbox.accepted.connect( self.accept)
        btnbox.rejected.connect( self.reject)
        layout.addWidget(btnbox)
        self.setLayout(layout)
    
    def exec_(self):
        ret = [super(AddServerDialog,self).exec_()]
        if ret[0] == QDialog.Accepted:
            ret += [
                str(self.name.text()),
                str(self.address.text()),
                int(self.port.text()) ]
        return ret

class ListPickerDialog(QDialog):
    def __init__(self,sel,parent=None):
        super(ListPickerDialog,self).__init__(parent)
        self.sel = sel

    def __del__(self):
        if self.sel.view():
            self.sel.view().setParent(None)

    def reject(self):
        if self.sel.view().currentIndex().row() == -1:
            self.sel.selected.emit("")
        super(ListPickerDialog,self).reject()

    def accept(self):
        mi = self.sel.view().currentIndex()
        if mi.flags() & Qt.ItemIsEnabled and mi.flags() & Qt.ItemIsSelectable:
            self.sel.setCurrentIndex( mi.row())
            self.sel.selected.emit(str(mi.data()))
            super(ListPickerDialog,self).accept()

class ServerPickSelector(ListPickSelector):
    def __init__(self,parent=None):
        super(ServerPickSelector,self).__init__(parent)
    
    def widget(self,parent):
        td = ListPickerDialog(self, parent)
        if isinstance(parent,QAbstractButton):
            td.setWindowTitle(parent.text())
        td.setAttribute(Qt.WA_DeleteOnClose)
        layout = QHBoxLayout();
        layout.setContentsMargins(16, 0, 16, 8)
        
        view = self.view()
        if not view:
            listView = QListView()
            listView.setModel(self.model())
            listView.setModelColumn(self.modelColumn())
            if listView.sizeHintForRow(0)>0:
                listView.setMinimumHeight(listView.sizeHintForRow(0) * 5)
            view = listView
        else:
            view.setModel(self.model())
        
        layout.addWidget(view)
        self.setView(view)
        
        if self.model():
            index = self.model().index(self.currentIndex(), self.modelColumn())
            self.selectModelIndex(index)
        
        btnbox = QDialogButtonBox(Qt.Vertical)
        btnbox.addButton("Select", QDialogButtonBox.AcceptRole)
        addBtn = btnbox.addButton("Add", QDialogButtonBox.ActionRole)
        addBtn.clicked.connect(self.addServer)
        editBtn = btnbox.addButton("Edit", QDialogButtonBox.ActionRole)
        editBtn.clicked.connect(self.editServer)
        remBtn = btnbox.addButton("Remove", QDialogButtonBox.ActionRole)
        remBtn.clicked.connect(self.remServer)
        btnbox.accepted.connect( td.accept)
        btnbox.rejected.connect( td.reject)
        layout.addWidget(btnbox)
        
        td.setLayout(layout)
        return td

    def selectModelIndex(self,index):
        self.view().setCurrentIndex(index)
        self.view().selectionModel().select(
            index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        self.view().scrollTo(index, QAbstractItemView.PositionAtCenter)
        

    def addServer(self):
        d = AddServerDialog()
        ret = d.exec_()
        if ret[0] != QDialog.Accepted: return
        name, address, port = ret[1:]
        if not (len(name) and len(address) and int(port) > 0):
            # report error
            return
        model = self.model()
        existingList = model.findItems(name)
        if not len(existingList):
            rowList = [QStandardItem(str(i)) for i in ret[1:]]
            model.appendRow(rowList)
            self.selectModelIndex(rowList[0].index())
        else:
            ans = QMessageBox.question(
                self.view(), "Edit %s" % str(name), "Edit existing entry?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ans == QMessageBox.Yes:
                row = existingList[0].row()
                for col in xrange(model.columnCount()):
                    model.item(row,col).setText( str(ret[col+1]))
                    self.selectModelIndex(existingList[0].index())
    
    def remServer(self):
        mi = self.view().currentIndex()
        row = mi.row()
        if row == -1: return
        ans = QMessageBox.question(
            self.view(), "Remove %s" % str(mi.data()), "Are you sure?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ans == QMessageBox.Yes:
            self.model().removeRows( row, 1)

    def editServer(self):
        mi = self.view().currentIndex()
        row = mi.row()
        if row == -1: return
        model = self.model()
        oldname, oldaddress, oldport = [
            model.item(mi.row(),col).text()
            for col in xrange(model.columnCount()) ]
        d = AddServerDialog(oldname, oldaddress, oldport)
        ret = d.exec_()
        if ret[0] == QDialog.Accepted:
            name, address, port = ret[1:]
            if len(name) and name != oldname:
                model.item(mi.row(),0).setText(name)
            if len(address) and address != oldaddress:
                model.item(mi.row(),1).setText(address)
            if port > 0 and port != oldport:
                model.item(mi.row(),2).setText(str(port))

class Prefs(QDialog):
    def __init__(self,data,parent=None):
        super(Prefs,self).__init__(parent)
        self.data = data
        self.initData()
        self.initGUI()

    def accept(self):
        self.data.selected    = str(self.serverBtn.valueText())
        self.data.autoconnect = bool(self.autoconnect.isChecked())
        super(Prefs,self).accept()
        
    def initData(self):
        self.serverSel = ServerPickSelector(self)
        self.serverSel.setModel(self.data.servers)
        self.serverSel.setModelColumn(0)
        selectedList = self.data.servers.findItems(self.data.selected)
        if len(selectedList):
            self.serverSel.setCurrentIndex( selectedList[0].row())
        self.serverBtn = ValueButton("Server")
        self.serverBtn.setPickSelector(self.serverSel)
        self.autoconnect = QCheckBox("Autoconnect")
        self.autoconnect.setChecked(self.data.autoconnect)

    def initGUI(self):
        layout = QHBoxLayout()
        preflayout = QVBoxLayout()
        preflayout.addWidget(self.serverBtn)
        preflayout.addWidget(self.autoconnect)
        layout.addLayout(preflayout)
        
        btnbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                                  Qt.Vertical)
        btnbox.accepted.connect( self.accept)
        btnbox.rejected.connect( self.reject)
        layout.addWidget(btnbox)
        self.setLayout(layout)
        self.setWindowTitle("Preferences")
