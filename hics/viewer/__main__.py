if __name__ == '__main__':
    import argparse
    from hics.viewer.mainwindow import ApplicationWindow
    from PyQt5 import QtWidgets
    import sys
    
    parser = argparse.ArgumentParser()    
    parser.add_argument('file', help = 'file to read')
    parser.add_argument('viewstate', help = 'view state file', nargs='?')
    
    args = parser.parse_args()
    
    if args.file.endswith('.viewstate') and args.viewstate is None:
        args.file, args.viewstate = None, args.file
    
    qApp = QtWidgets.QApplication(sys.argv)
    
    
    aw = ApplicationWindow(args.file, args.viewstate)
    aw.show()
    sys.exit(qApp.exec_())
