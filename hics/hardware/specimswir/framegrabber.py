import socket
import threading
import struct
import redis
import numpy
import pickle

class FrameGrabber(threading.Thread):
    _debug = False
    _redis_expire = 10
    _wavelengths = [937.06,943.47,949.88,956.28,962.69,969.10,975.50,981.91,988.31,994.71,1001.11,1007.51,1013.91,1020.31,1026.71,1033.11,1039.50,1045.90,1052.29,1058.68,1065.07,1071.46,1077.85,1084.24,1090.63,1097.02,1103.40,1109.79,1116.17,1122.55,1128.93,1135.31,1141.69,1148.07,1154.45,1160.83,1167.20,1173.58,1179.95,1186.32,1192.69,1199.07,1205.44,1211.80,1218.17,1224.54,1230.90,1237.27,1243.63,1250.00,1256.36,1262.72,1269.08,1275.44,1281.80,1288.15,1294.51,1300.86,1307.22,1313.57,1319.92,1326.27,1332.62,1338.97,1345.32,1351.67,1358.02,1364.36,1370.70,1377.05,1383.39,1389.73,1396.07,1402.41,1408.75,1415.09,1421.42,1427.76,1434.09,1440.43,1446.76,1453.09,1459.42,1465.75,1472.08,1478.41,1484.73,1491.06,1497.38,1503.71,1510.03,1516.35,1522.67,1528.99,1535.31,1541.63,1547.94,1554.26,1560.57,1566.89,1573.20,1579.51,1585.82,1592.13,1598.44,1604.75,1611.06,1617.36,1623.67,1629.97,1636.27,1642.57,1648.88,1655.18,1661.47,1667.77,1674.07,1680.37,1686.66,1692.95,1699.25,1705.54,1711.83,1718.12,1724.41,1730.70,1736.98,1743.27,1749.56,1755.84,1762.12,1768.41,1774.69,1780.97,1787.25,1793.52,1799.80,1806.08,1812.35,1818.63,1824.90,1831.17,1837.45,1843.72,1849.98,1856.25,1862.52,1868.79,1875.05,1881.32,1887.58,1893.84,1900.10,1906.37,1912.62,1918.88,1925.14,1931.40,1937.65,1943.91,1950.16,1956.41,1962.67,1968.92,1975.17,1981.42,1987.66,1993.91,2000.16,2006.40,2012.64,2018.89,2025.13,2031.37,2037.61,2043.85,2050.09,2056.32,2062.56,2068.79,2075.03,2081.26,2087.49,2093.72,2099.95,2106.18,2112.41,2118.64,2124.87,2131.09,2137.31,2143.54,2149.76,2155.98,2162.20,2168.42,2174.64,2180.86,2187.07,2193.29,2199.50,2205.72,2211.93,2218.14,2224.35,2230.56,2236.77,2242.97,2249.18,2255.39,2261.59,2267.79,2274.00,2280.20,2286.40,2292.60,2298.80,2304.99,2311.19,2317.39,2323.58,2329.78,2335.97,2342.16,2348.35,2354.54,2360.73,2366.92,2373.10,2379.29,2385.47,2391.66,2397.84,2404.02,2410.20,2416.38,2422.56,2428.74,2434.92,2441.09,2447.27,2453.44,2459.61,2465.79,2471.96,2478.13,2484.30,2490.46,2496.63,2502.80,2508.96,2515.13,2521.29,2527.45,2533.61,2539.77]
    
    def __init__(self, redis_conn, tcp_port):
        threading.Thread.__init__(self, name="FrameGrabber")
        
        if tcp_port is None:
            tcp_port = 1234
        self._redis = redis_conn
        assert isinstance(redis_conn, redis.client.Redis)
        
        self._listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listen_sock.bind(('', tcp_port))
        self._listen_sock.listen(1)
        self._listen_sock.settimeout(1)
        
        self._continue = True
        
    def run(self):
        self._redis.set('hscc:framegrabber:wavelengths', ','.join('{0:0.02f}'.format(x) for x in self._wavelengths))
        
        frame_header = struct.Struct('<L')
        first_frame = True
        
        while self._continue:
            try:
                conn, addr = self._listen_sock.accept()
            except socket.timeout:
                #Give a change to abort the loop
                continue
            if self._debug:
                print('Connected by', addr)
                
            conn.settimeout(1)
            
            while self._continue:
                try:
                    header_data = conn.recv(frame_header.size)
                except socket.timeout:
                    continue #Give a change to abort the loop
                except:
                    break
                if not header_data:
                    break
                length = frame_header.unpack(header_data)[0]
    
                data = b''
                while len(data) < length and self._continue:
                    try:
                        packet_data = conn.recv(length - len(data))
                    except socket.timeout:
                        continue #Give a change to abort the loop                    
                    except:
                        break
                    if not packet_data:
                        break
                    data += packet_data
                    
                #Abort if we need to stop
                if not self._continue:
                    break
                    
                #Ignore first frame (may be broken)
                if first_frame:
                    first_frame = False
                    continue
                
                try:
                    matrix = numpy.fromstring(data, dtype = numpy.uint16)
                    matrix.resize((256, 320))
                    matrix = numpy.flipud(numpy.rollaxis(matrix.reshape((1, 256, 320)), 2, 0))[:, :, ::-1]
                    self._redis.publish('hscc:framegrabber:frame_raw', pickle.dumps(matrix))
                    
                except Exception as e:
                    print(e)
            
        self._redis.delete('hscc:framegrabber:wavelengths')
        
    def stop(self, dummy=None):
        self._continue = False

if __name__ == '__main__':
    import redis, argparse, time, signal
    parser = argparse.ArgumentParser()
    parser.add_argument("--redis", help="Redis URL")
    parser.add_argument("--port", help="TCP/IP port")
    args = parser.parse_args()
    if args.redis is not None:
        r = redis.from_url(args.redis)
    else:
        r = redis.Redis()
        
    framegrabber = FrameGrabber(r, args.port)
    framegrabber.run()
    
    def stop_thread(*a):
        framegrabber.stop()
        
    signal.signal(signal.SIGINT, stop_thread)
    signal.signal(signal.SIGTERM, stop_thread)

    while True:
        time.sleep(1)
