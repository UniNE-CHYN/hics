
import pickle

import numpy


from hics.utils.plugin import BaseImperativePlugin
class LabelPrint(BaseImperativePlugin):
    plugin_name = 'Print label'
    plugin_key = 'labelprint'
    plugin_input = []
    plugin_output = []
    plugin_output_captions =  []
    
    plugin_uses = []
    plugin_listens = []
    plugin_requires_lock = False
    
    plugin_input_before = ['string:192.168.1.6', 'integerspinbox:1:100:1', 'string:N', 'string:0000']
    plugin_input_before_captions = ['IP address', 'Template number','Field name', 'Text']
    
    _area = 0.3
    
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._frame_rate = 100
    
    def start(self):
        self._ip = self._input_before[0].decode('utf8').strip()
        self._template_number = int(self._input_before[1].decode('utf8').strip())
        self._field_name = self._input_before[2].decode('utf8').strip()
        self._text = self._input_before[3].decode('utf8').strip()
        
        super().start()
    
    def _run(self):
        import socket, struct, time
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._ip, 9100))
        
        sock.send(b'\x1bia3') #Template mode
        sock.send(b'^II') #Template mode
        sock.send(b'^TS'+'{0:03d}'.format(self._template_number).encode('ascii')) #Choose template
        sock.send(b'^ON'+self._field_name.encode('ascii')+b'\x00') #Select field
        sock.send(b'^DI'+struct.pack('<h', len(self._text)) + self._text.encode('ascii')) #Set data
        sock.send(b'^FF') #Print
        sock.close()
        
        
    
if __name__ == '__main__':
    LabelPrint.main()

