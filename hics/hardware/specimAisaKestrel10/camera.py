import numpy
import threading
import redis
import time
import pickle
import scipy.ndimage
import ctypes
import struct

from hics.utils.redis import RedisLink, RedisNotifier

class AisaKestrelFramegrabber(threading.Thread):
    wavelengths = [394.70, 396.39, 398.07, 399.76, 401.44, 403.13, 404.82, 406.50, 408.19, 409.88, 411.57, 413.25, 414.94, 416.63, 418.32, 420.01, 421.70, 423.39, 425.08, 426.77, 428.47, 430.16, 431.85, 433.54, 435.24, 436.93, 438.62, 440.32, 442.01, 443.71, 445.40, 447.10, 448.79, 450.49, 452.18, 453.88, 455.58, 457.28, 458.97, 460.67, 462.37, 464.07, 465.77, 467.47, 469.16, 470.86, 472.56, 474.26, 475.97, 477.67, 479.37, 481.07, 482.77, 484.47, 486.18, 487.88, 489.58, 491.28, 492.99, 494.69, 496.40, 498.10, 499.81, 501.51, 503.22, 504.92, 506.63, 508.33, 510.04, 511.74, 513.45, 515.16, 516.87, 518.57, 520.28, 521.99, 523.70, 525.41, 527.11, 528.82, 530.53, 532.24, 533.95, 535.66, 537.37, 539.08, 540.79, 542.50, 544.22, 545.93, 547.64, 549.35, 551.06, 552.77, 554.49, 556.20, 557.91, 559.63, 561.34, 563.05, 564.77, 566.48, 568.19, 569.91, 571.62, 573.34, 575.05, 576.77, 578.48, 580.20, 581.91, 583.63, 585.34, 587.06, 588.78, 590.49, 592.21, 593.93, 595.64, 597.36, 599.08, 600.80, 602.51, 604.23, 605.95, 607.67, 609.39, 611.10, 612.82, 614.54, 616.26, 617.98, 619.70, 621.42, 623.14, 624.86, 626.58, 628.30, 630.02, 631.74, 633.46, 635.18, 636.90, 638.62, 640.34, 642.06, 643.78, 645.50, 647.22, 648.94, 650.67, 652.39, 654.11, 655.83, 657.55, 659.28, 661.00, 662.72, 664.44, 666.16, 667.89, 669.61, 671.33, 673.05, 674.78, 676.50, 678.22, 679.95, 681.67, 683.39, 685.12, 686.84, 688.56, 690.29, 692.01, 693.73, 695.46, 697.18, 698.91, 700.63, 702.35, 704.08, 705.80, 707.53, 709.25, 710.97, 712.70, 714.42, 716.15, 717.87, 719.60, 721.32, 723.04, 724.77, 726.49, 728.22, 729.94, 731.67, 733.39, 735.12, 736.84, 738.57, 740.29, 742.02, 743.74, 745.47, 747.19, 748.92, 750.64, 752.36, 754.09, 755.81, 757.54, 759.26, 760.99, 762.71, 764.44, 766.16, 767.89, 769.61, 771.34, 773.06, 774.79, 776.51, 778.24, 779.96, 781.69, 783.41, 785.13, 786.86, 788.58, 790.31, 792.03, 793.76, 795.48, 797.20, 798.93, 800.65, 802.38, 804.10, 805.83, 807.55, 809.27, 811.00, 812.72, 814.44, 816.17, 817.89, 819.62, 821.34, 823.06, 824.79, 826.51, 828.23, 829.95, 831.68, 833.40, 835.12, 836.85, 838.57, 840.29, 842.01, 843.74, 845.46, 847.18, 848.90, 850.62, 852.35, 854.07, 855.79, 857.51, 859.23, 860.95, 862.68, 864.40, 866.12, 867.84, 869.56, 871.28, 873.00, 874.72, 876.44, 878.16, 879.88, 881.60, 883.32, 885.04, 886.76, 888.48, 890.20, 891.92, 893.64, 895.35, 897.07, 898.79, 900.51, 902.23, 903.95, 905.66, 907.38, 909.10, 910.82, 912.53, 914.25, 915.97, 917.68, 919.40, 921.12, 922.83, 924.55, 926.26, 927.98, 929.69, 931.41, 933.12, 934.84, 936.55, 938.27, 939.98, 941.70, 943.41, 945.12, 946.84, 948.55, 950.26, 951.98, 953.69, 955.40, 957.11, 958.82, 960.54, 962.25, 963.96, 965.67, 967.38, 969.09, 970.80, 972.51, 974.22, 975.93, 977.64, 979.35, 981.06, 982.77, 984.48, 986.18, 987.89, 989.60, 991.31, 993.01, 994.72, 996.43, 998.13, 999.84, 1001.55, 1003.25]
    frameheight = 2048
    max_pixel_value = 4095
    
    def __init__(self, system):
        threading.Thread.__init__(self, name=self.__class__.__name__)
        self._system = system
        
    @property
    def _redis(self):
        return self._system._redis
    
    @property
    def _epix(self):
        return self._system._epix
    
    def run(self):
        """Run the thread"""
        self._redis.set(
            'hics:framegrabber:wavelengths',
            ','.join('{0:0.02f}'.format(x) for x in self.wavelengths)
        )
        
        self._redis.set(
            'hics:framegrabber:frameheight',
            self.frameheight
        )
        
        self._redis.set(
            'hics:framegrabber:max_pixel_value',
            self.max_pixel_value
        )
        
        old_buffer_number = None
        
        xdim = self._epix.pxd_imageXdim()
        ydim = self._epix.pxd_imageYdim()

        imagesize = xdim*ydim
        c_buf = (ctypes.c_ushort * imagesize)(0)
        
        self._epix.pxd_goLivePair(0x1, 1, 2)
        
        t=time.time()
        while self._system.running:
            buffer_number = self._epix.pxd_capturedBuffer(1)
            if buffer_number == old_buffer_number:
                time.sleep(0.01)
                continue
            
            #print(buffer_number, 1/(time.time()-t+0.0001))
            t=time.time()
                
            old_buffer_number = buffer_number
                
            self._epix.pxd_readushort(0x1, buffer_number, 0, 0, -1, ydim, c_buf, ctypes.sizeof(c_buf), b"Gray")
            im = numpy.frombuffer(c_buf, ctypes.c_ushort).reshape([xdim, ydim])
            im = im[:352][::-1,::-1].T
            im = im[:, numpy.newaxis, :]
            
            self._redis.publish('hics:framegrabber:frame_raw', pickle.dumps(im))
            
        self._epix.pxd_goUnLive(0x1);

        self._redis.delete('hics:framegrabber:wavelengths')
        self._redis.delete('hics:framegrabber:frameheight')
        self._redis.delete('hics:framegrabber:max_pixel_value')
        
        
class AisaKestrelCamera:
    _shutter_latency = 1
    
    def __init__(self, system):
        self._system = system
        
        self._switch_to_ascii_mode()
        
        #Set internal trigger source
        self._write_addr_int(44,0)
        #Set Tigger.CFR
        self._write_addr_int(51,1)
        
        self.shutter_open = True
        self.frame_rate = 6
        self.integration_time = 20000
        
    def _switch_to_ascii_mode(self):
        c_buf=(ctypes.c_char * 20)(0)
        self._epix.pxd_serialWrite(0x1, 0, bytes([2]), 1)
        time.sleep(1)
        self._epix.pxd_serialRead(0x1, 0, c_buf, 20)
        #Should return ok
        assert c_buf.raw[0] == 0x02
        
    def _read_addr(self, addr):
        c_buf=(ctypes.c_char * 20)(0)
        self._epix.pxd_serialWrite(0x1, 0, b'\x52'+struct.pack('>I',addr)+b'\x72', 6)
        time.sleep(0.1)
        retlen = self._epix.pxd_serialRead(0x1, 0, c_buf, 20)
        assert retlen == 6
        ret=c_buf.raw[:6]
        assert ret[0]==0x72
        assert ret[5]==0x72
        return ret[1:-1]
        
    def _write_addr(self, addr, data):
        assert addr in (44, 1, 3, 481, 51), "Invalid addr {}".format(addr)
        assert type(data)==bytes
        assert len(data)==4
        
        c_buf=(ctypes.c_char * 20)(0)
        self._epix.pxd_serialWrite(0x1, 0, b'\x57'+struct.pack('>I',addr) + data+b'\x77', 10)
        time.sleep(0.1)
        retlen = self._epix.pxd_serialRead(0x1, 0, c_buf, 20)
        assert retlen == 1
        assert c_buf.raw[0]==0x77

    def _read_addr_float(self, addr):
        return struct.unpack('>f', self._read_addr(addr))[0]
        
    def _write_addr_float(self, addr, data):
        return self._write_addr(addr, struct.pack('>f', data))
        
    def _read_addr_int(self, addr):
        return struct.unpack('>I', self._read_addr(addr))[0]
        
    def _write_addr_int(self, addr, data):
        return self._write_addr(addr, struct.pack('>I', data))
        
    @property
    def _redis(self):
        return self._system._redis
    
    @property
    def _epix(self):
        return self._system._epix
    
    @property
    def frame_rate(self):
        return int(1000/self._read_addr_float(3))
    
    @frame_rate.setter
    def frame_rate(self, new_frame_rate):
        self._write_addr_float(3, 1000/float(new_frame_rate))
        
    @property
    def frame_rate_min(self):
        return 1
    
    @property
    def frame_rate_max(self):
        return int(self._read_addr_float(446))
        
    @property
    def shutter_open(self):
        #FIXME!!!
        return self._shutter_open
    
    @shutter_open.setter
    def shutter_open(self, new_shutter_open):
        #FIXME!!!
        new_shutter_open = self._to_bool(new_shutter_open)
        self._shutter_open = {True: 1, False: 0}[new_shutter_open]
        
    @property
    def shutter_latency(self):
        return self._shutter_latency
        
    @property
    def integration_time(self):
        return self._read_addr_float(1) * 1000.
    
    @integration_time.setter
    def integration_time(self, new_integration_time):
        self._write_addr_float(1, float(new_integration_time)/1000)
            
    @property
    def integration_time_min(self):
        return 1
    
    @property
    def integration_time_max(self):
        return 200000
        
    @property
    def nuc(self):
        return 0
        
    @nuc.setter
    def nuc(self, new_value):
        return #Do nothing
            
        
    def _to_bool(self, v):
        if type(v) == bytes:
            return v == b'1'
        elif type(v) == str:
            return v == '1'
        elif type(v) == int:
            return v == 1
        elif type(v) == bool:
            return v
        else:
            raise ValueError("Unknown value type {0!r}".format(v))
    
    def notify(self, prop):
        return
            

class AisaKestrelSystem(threading.Thread):
    def __init__(self, redis_conn, args):
        threading.Thread.__init__(self, name="AisaKestrelSystem")

        self._redis = redis_conn
        assert isinstance(redis_conn, redis.client.Redis)
        self._continue = True
        
        self._epix = ctypes.windll.LoadLibrary(args.xclib)
        
        if self._epix.pxd_PIXCIopen(b"",b"",args.fmt.encode('ascii')) != 0:
            self._epix.pxd_mesgFault(1)
            sys.exit(1)
        
        self._camera = AisaKestrelCamera(self)
        self._framegrabber = AisaKestrelFramegrabber(self)
        
    def run(self):
        self._framegrabber.start()
        redis_link_camera = RedisLink(self._redis, 'hics:camera', self._camera)
        
        
        while self.running:
            time.sleep(1)
            
        redis_link_camera.stop()

    def stop(self):
        """Stop the thread"""
        self._continue = False

    @property
    def running(self):
        return self._continue
    
def add_arguments(parser):
	parser.add_argument('--xclib', help='EPIX XCLIB path', default="C:\\Program Files\\Specim\\Lumo - Recorder\\2018_512\\XCLIBW64.dll")
	parser.add_argument('--fmt', help='EPIX format file', default="C:\\Users\\Public\\Documents\\Specim\\External\\Epix\\Specim_Kestrel10.fmt")
    
def launch(redis_client, args):
    aks = AisaKestrelSystem(redis_client, args)
    aks.start()
    return aks

def main():
    from hics.utils.daemonize import stdmain
    return stdmain(cb_launch=launch, cb_add_arguments_to_parser=add_arguments)

if __name__ == '__main__':
    main()
