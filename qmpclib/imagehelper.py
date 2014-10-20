import sip
sip.setapi('QVariant', 2)

from PyQt4.QtCore import QSettings
from PyQt4.QtGui  import QPixmap, QIcon, QApplication

import os

class ImageHelper(object):
    def __init__(self,images={},icons={}):
        self.__images__ = images
        self.__icons__  = icons

    def __getattr__(self,name):
        if self.__images__.has_key(name):
            return self.findImage(name)
        
        if self.__icons__.has_key(name):
            return self.findIcon(name)
        
    def findImage(self,name):
        uri = self.__images__.get(name,None)
        if not uri:
            print "No URI for image", name
            return QPixmap()
        
        # try filesystem
        path = self.findPath(uri)
        if len(path): return QPixmap(path)
        
        # try datadir
        path = self.findDataDir(uri)
        if len(path): return QPixmap(path)
        
        print "Image not found:", name
        return QPixmap()

    def findIcon(self,name):
        uri = self.__icons__.get(name,None)
        if not uri:
            print "No URI for icon", name
            return QIcon()
        
        # try filesystem
        path = self.findPath(uri)
        if len(path): return QIcon(path)
        
        # try Qt icon theme
        icon = QIcon.fromTheme(uri)
        if not icon.isNull(): return icon

        if os.path.isabs(uri):
            path = os.path.join('icons',os.path.basename(uri))
            if os.path.exists(path): return QIcon(path)
        else:
            path = os.path.join('icons',uri)
            ext = os.path.splitext(path)[1]
            if not len(ext): path += '.png'
            if os.path.exists(path): return QIcon(path)
        
        # print warning and return empty icon
        print "Icon not found:", name
        return icon
    
    def findPath(self,path):
        if os.path.exists(path): return path
        else: return ''
    
    def findDataDir(self,name):
        if not len(QApplication.applicationName()):
            print "QApplication.applicationName() is not set"
            return ''
        s = QSettings()
        if s.contains('datadir'):
            datadir   = unicode(s.value('datadir'))
            imagepath = os.path.join(datadir,name)
            if os.path.exists(imagepath):
                return imagepath
        else:
            dirname = os.path.dirname(name)
            datadirsuffix = os.path.join(
                'share',unicode(QApplication.applicationName()))
            dirpath = os.path.normpath(os.path.join(datadirsuffix,dirname))
            for root, dirs, files in os.walk('/usr', None, True):
                if not root.endswith(dirpath): continue
                for f in files:
                    filepath = os.path.join(root,f)
                    if filepath.endswith(name):
                        pos = filepath.find(name)
                        if pos == -1: continue
                        datadir = os.path.normpath(root[:pos])
                        s.setValue('datadir',datadir)
                        return filepath
        return ''
