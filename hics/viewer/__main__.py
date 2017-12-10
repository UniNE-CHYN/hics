if __name__ == '__main__':
    from hics.viewer.mainwindow import ApplicationWindow
    from PyQt5 import QtWidgets
    import sys
    qApp = QtWidgets.QApplication(sys.argv)
    
    aw = ApplicationWindow(sys.argv[1])
    aw.show()
    sys.exit(qApp.exec_())
