from PyQt4.Qt import *

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
            datadir   = s.value('datadir')
            imagepath = os.path.join(datadir,name)
            if os.path.exists(imagepath):
                return imagepath
        else:
            datadirsuffix = os.path.join('share',unicode(QApplication.applicationName()))
            for root, dirs, files in os.walk('/usr', None, True):
                if not root.endswith(datadirsuffix): continue
                for d in dirs:
                    for f in files:
                        if os.path.join(d,f) == name:
                            s.setValue('datadir',root)
                            return os.path.join(root,name)
        return ''
