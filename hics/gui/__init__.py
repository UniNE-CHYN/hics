def run():
    import sys
    from PyQt4 import QtGui, QtCore
    from .mainwindow import MainWindow    

    QtCore.QCoreApplication.setOrganizationName("Université de Neuchâtel")
    QtCore.QCoreApplication.setOrganizationDomain("unine.ch")
    QtCore.QCoreApplication.setApplicationName("Hyperspectral Imaging Control System")
    
    app = QtGui.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())    
