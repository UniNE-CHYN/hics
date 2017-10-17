from PyQt4 import QtGui, QtCore

class QSpectrumWidget(QtGui.QGraphicsView):
    mousedownat = QtCore.pyqtSignal(int, float)
    
    def __init__(self, *a, **kw):
        QtGui.QGraphicsView.__init__(self, *a, **kw)
        self.setMouseTracking(True)
        self._last_pos = None
        
    
    def mousePressEvent(self, ev):
        pos = self.mapToScene(ev.pos())
        if ev.buttons() == QtCore.Qt.LeftButton:
            pos = int(round(pos.x())), pos.y()
            self.mousedownat.emit(*pos)
            self._last_pos = pos
            
        
    def mouseMoveEvent(self, ev):
        assert isinstance(ev, QtGui.QMouseEvent)
        pos = self.mapToScene(ev.pos())
        if ev.buttons() == QtCore.Qt.LeftButton:
            pos = int(round(pos.x())), pos.y()
            if pos[0] != self._last_pos[0]:
                dy = (pos[1] - self._last_pos[1]) / (pos[0] - self._last_pos[0])
            else:
                dy = 0
            if pos[0] > self._last_pos[0]:
                sgn = 1
            else:
                sgn = -1
            for x in range(self._last_pos[0], pos[0] + 1, sgn):
                self.mousedownat.emit(x, self._last_pos[1] + dy * (x - self._last_pos[0]))
            self._last_pos = pos
            
        
