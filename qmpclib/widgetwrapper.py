try:
    from PyQt4.QtMaemo5 import QMaemo5ValueButton      as ValueButton
    from PyQt4.QtMaemo5 import QMaemo5ListPickSelector as ListPickSelector
except:
    # TODO: implement for other platforms (or maybe rewrite code using
    #       standard widgets)
    print "This software requires QMaemo5 libraries, exiting"
    import sys
    sys.exit(1)
