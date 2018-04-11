import scipy.ndimage
from mmappickle import mmapdict
import numpy
from matplotlib import pyplot as plt
import hics.utils.datafile

class AutoMaskAlgorithm:
    def __init__(self, data, maskspec):
        self._data = data
        
    @property
    def data(self):
        return self._data
    
    @property
    def data_scalar(self):
        return numpy.log(self._data.mean(2))
        
        
class SimplyConnectedDistanceAutoMaskAlgorithm(AutoMaskAlgorithm):
    def __init__(self, data, maskspec):
        super().__init__(data, maskspec)
        
        self._norm_data = (data - data.mean(2)[:,:,numpy.newaxis]) / data.std(2)[:,:,numpy.newaxis]
        
        if maskspec is None:
            self._maskspec = []
        elif type(maskspec) == list:
            if type(maskspec)[0] == str:
                maskspec = [x.split(',') for x in args.maskspec]
                maskspec = [(int(x), int(y), float(z)) for x, y, z in maskspec]
            self._maskspec = maskspec
            
        self._cache_score = []
        self._cache_mask = {}
        self._current_point_id = None        
            
    def get_mask(self):
        mask = numpy.zeros(self._data.shape[:2])
        
        for point_id, mask_spec in enumerate(self._maskspec):
            if tuple(mask_spec) not in self._cache_mask:
                x, y, tolerance = mask_spec
                if len(self._cache_score) <= point_id:
                    delta = (numpy.abs(self._norm_data - self._norm_data[y,x,numpy.newaxis,numpy.newaxis])).sum(2)
                    delta -= delta.min()
                    delta /= delta.max()
                    delta = (1 - delta)
                    self._cache_score.append(delta)
                    
                
                point_mask, _dummy = scipy.ndimage.label(self._cache_score[point_id] >= tolerance)
                self._cache_mask[tuple(mask_spec)] = scipy.ndimage.binary_fill_holes(point_mask==point_mask[y, x])
                
            mask += self._cache_mask[tuple(mask_spec)]
        
        return scipy.ndimage.binary_fill_holes(mask > 0)
    
    def get_maskspec_arg(self):
        return ['{},{},{}'.format(x, y, z) for x, y, z in self._maskspec]
    
    def mpl_init_structures(self, ax):
        self._mpl_mask_im = numpy.zeros(self._data.shape[:2]+(4, ))
        self._mpl_mask_im[:, :, 0] = 1
        self._mpl_mask = ax.imshow(self._mpl_mask_im)
        self._mpl_maskpoints, = ax.plot([], [], 'o', picker=5)
        
    def mpl_update_plot(self):
        #Update mask (alpha channel)
        self._mpl_mask_im[:, :, 3] = (self.get_mask() == 0) * 0.2
        self._mpl_mask.set_data(self._mpl_mask_im)
        
        #Update maskpoints
        self._mpl_maskpoints.set_data([x[0] for x in self._maskspec], [x[1] for x in self._maskspec])
        
    def mpl_pick_object(self, event):
        #Returns True if an object was clicked on, False otherwise
        #Logic is that the canvas must ignore the mousedown if an object was selected
        self._current_point_id = None
        
        if event.artist != self._mpl_maskpoints:
            return False
        
        for point_id in sorted(event.ind, reverse=True):
            self._maskspec.pop(point_id)
            self._cache_score.pop(point_id)
            
        return True
    
    def mpl_on_press(self, event):
        #Return True if something changed, False otherwise
        self._current_point_id = None
        
        xp = int(event.xdata)
        yp = int(event.ydata)
        if xp < 0 or xp >= self._data.shape[1]:
            return False
        if yp < 0 or yp >= self._data.shape[0]:
            return False
        
        self._maskspec.append([xp, yp, 1])
        self._current_point_id = len(self._maskspec) - 1
        
        return True
    
    def mpl_on_release(self, event):
        self._current_point_id = None
        
        return False
    
    def mpl_on_motion(self, event):
        if self._current_point_id is None:
            return False
        
        xp, yp, sc = self._maskspec[self._current_point_id]
        
        delta = numpy.linalg.norm(numpy.array([event.xdata-xp, event.ydata-yp]))
        new_sc = 1 - numpy.clip(2*delta/min([self._data.shape[0], self._data.shape[1]]), 0, 1)
        self._maskspec[self._current_point_id][2] = round(new_sc, 2)
        return True
    
    
class NearestMaskAlgorithm(AutoMaskAlgorithm):
    def __init__(self, data, maskspec):
        super().__init__(data, maskspec)
        
        self._norm_data = (data - data.mean(2)[:,:,numpy.newaxis]) / data.std(2)[:,:,numpy.newaxis]
        
        if maskspec is None:
            self._maskspec = []
        elif type(maskspec) == list:
            if type(maskspec)[0] == str:
                maskspec = [x.split(',') for x in args.maskspec]
                maskspec = [(int(x), int(y), bool(z)) for x, y, z in maskspec]
            self._maskspec = maskspec
            
        self._cache_score = []
        self._cache_distance = {}
        self._current_point_id = None        
            
    def get_mask(self):
        if len(self._maskspec) == 0:
            return numpy.zeros(self._data.shape[:2], dtype=numpy.bool)
        
        for point_id, mask_spec in enumerate(self._maskspec):
            if tuple(mask_spec) not in self._cache_distance:
                x, y, in_mask = mask_spec
                
                point_sp = self._norm_data[y, x]
                self._cache_distance[tuple(mask_spec)] = (numpy.abs(self._norm_data - self._norm_data[y,x,numpy.newaxis,numpy.newaxis])).sum(2)
                
        distances = numpy.zeros(self._data.shape[:2]+(len(self._maskspec), ))
        in_mask_list = numpy.zeros((len(self._maskspec), ), dtype=numpy.bool)
        for point_id, mask_spec in enumerate(self._maskspec):
            distances[:, :, point_id] = self._cache_distance[tuple(mask_spec)]
            in_mask_list[point_id] = mask_spec[2]
            
        best_distances = distances.argmin(2)
        mask = in_mask_list[best_distances]
        
        mask = mask > 0
        mask = scipy.ndimage.binary_fill_holes(mask)
        
        #Keep only areas which contain a selected point
        mask_cc, _dummy = scipy.ndimage.label(mask)
        mask = numpy.zeros(self._data.shape[:2], dtype=numpy.bool)
        for k in  self._maskspec:
            if k[2]:
                mask[mask_cc==mask_cc[k[1], k[0]]] = True
        
        
        return mask
    
    def get_maskspec_arg(self):
        return ['{},{},{}'.format(x, y, int(z)) for x, y, z in self._maskspec]
    
    def mpl_init_structures(self, ax):
        self._mpl_mask_im = numpy.zeros(self._data.shape[:2]+(4, ))
        self._mpl_mask_im[:, :, 0] = 1
        self._mpl_mask = ax.imshow(self._mpl_mask_im)
        self._mpl_maskpoints_in, = ax.plot([], [], 'ob', picker=5)
        self._mpl_maskpoints_out, = ax.plot([], [], 'or', picker=5)
        
    def mpl_update_plot(self):
        #Update mask (alpha channel)
        self._mpl_mask_im[:, :, 3] = (self.get_mask() == 0) * 0.2
        self._mpl_mask.set_data(self._mpl_mask_im)
        
        #Update maskpoints
        self._mpl_maskpoints_in.set_data([x[0] for x in self._maskspec if x[2]], [x[1] for x in self._maskspec if x[2]])
        self._mpl_maskpoints_out.set_data([x[0] for x in self._maskspec if not x[2]], [x[1] for x in self._maskspec if not x[2]])
        
    def mpl_pick_object(self, event):
        #Returns True if an object was clicked on, False otherwise
        #Logic is that the canvas must ignore the mousedown if an object was selected
        if event.artist != self._mpl_maskpoints_in and event.artist != self._mpl_maskpoints_out:
            return False
        
        
        
        for point_id in sorted(event.ind, reverse=True):
            if event.artist == self._mpl_maskpoints_in:
                p = [x for x in self._maskspec if x[2]][point_id]
            else:
                p = [x for x in self._maskspec if not x[2]][point_id]
            point_id = self._maskspec.index(p)                
            
            self._maskspec.pop(point_id)
            
        return True
    
    def mpl_on_press(self, event):
        #Return True if something changed, False otherwise
        if event.button is None:
            return False
        xp = int(event.xdata)
        yp = int(event.ydata)
        if xp < 0 or xp >= self._data.shape[1]:
            return False
        if yp < 0 or yp >= self._data.shape[0]:
            return False
        
        self._maskspec.append([xp, yp, event.button == 1])
        
        return True
    
    def mpl_on_release(self, event):
        return False
    
    def mpl_on_motion(self, event):
        return self.mpl_on_press(event)
        #return False
    

class AutomaskGUI:
    def __init__(self, automask_algorithm):
        import matplotlib.pyplot as plt
        
        self._automask_algorithm = automask_algorithm


        
        self._mpl_ignore_press = False
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title('click and drag to add region to mask')
    
        #Draw the figure!
        meandata = self._automask_algorithm.data_scalar
        ax.imshow(meandata, cmap='gray', clim=(numpy.percentile(meandata.flatten(), 1), numpy.percentile(meandata.flatten(), 99)))
    
        self._automask_algorithm.mpl_init_structures(ax)
        
        fig.canvas.mpl_connect('pick_event', self._mpl_on_pick)
        fig.canvas.mpl_connect('button_press_event', self._mpl_on_press)
        fig.canvas.mpl_connect('button_release_event', self._mpl_on_release)
        fig.canvas.mpl_connect('motion_notify_event', self._mpl_on_motion) 
    
        self._mpl_fig = fig
        self._mpl_update_plot()
    
        plt.show()            
        
    def _mpl_on_pick(self, event):
        if self._automask_algorithm.mpl_pick_object(event):
            self._mpl_update_plot()
            self._mpl_ignore_press = True            
        
        return True
        
    def _mpl_on_press(self, event):
        if self._mpl_ignore_press:
            self._mpl_ignore_press = False
            return True
        
        
        if self._automask_algorithm.mpl_on_press(event):
            self._mpl_update_plot()
        
    def _mpl_on_release(self, event):
        if self._automask_algorithm.mpl_on_release(event):
            self._mpl_update_plot()
        
    def _mpl_on_motion(self, event):
        if self._automask_algorithm.mpl_on_motion(event):
            self._mpl_update_plot()
        

        
    def _mpl_update_plot(self):
        self._automask_algorithm.mpl_update_plot()
        self._mpl_fig.canvas.draw()
        

if __name__ == '__main__':
    import argparse, sys
    
    parser = argparse.ArgumentParser()    
    parser.add_argument('--input', help = 'input file', metavar='file.hdr', required = True)
    parser.add_argument('--output', help = 'output file', metavar='file.mhdr', required=True)
    parser.add_argument('--maskspec', help = 'Mask specification', metavar='maskspec', nargs='+', required=False)
    parser.add_argument('--method', help='Method to use', choices=('click', 'clickdrag'), default='click')
    parser.add_argument('--nocrop', help = 'Do not crop output', action='store_true')
    
    args = parser.parse_args()
    
    input_data = mmapdict(args.input, True)
    
    if args.method == 'click':
        algo = NearestMaskAlgorithm(input_data['hdr'], args.maskspec)
    elif args.method == 'clickdrag':
        algo = SimplyConnectedDistanceAutoMaskAlgorithm(input_data['hdr'], args.maskspec)
    
    
   
    if args.maskspec is None:
        #Run in interactive mode...
        am = AutomaskGUI(algo)
        
        args.maskspec = algo.get_maskspec_arg()

    input_data, output_data =  hics.utils.datafile.migrate_base_data(args, 'hics.datafile.maskdataauto')
        
    mask = ~algo.get_mask()
    cols = numpy.nonzero(mask.sum(0) != mask.shape[0])[0]
    rows = numpy.nonzero(mask.sum(1) != mask.shape[1])[0]
    
    for k in ('hdr', 'hdr-var'):
        if k in input_data.keys():
            data = numpy.ma.masked_invalid(input_data[k].copy())
            if hasattr(data, "mask"):
                data.mask = numpy.logical_or(data.mask, mask[:, :, numpy.newaxis].repeat(data.mask.shape[2], 2))
            #Crop if needed
            if not args.nocrop:
                data = data[rows.min():rows.max()+1, cols.min():cols.max()+1]
            output_data[k] = data
            
    output_data.vacuum()
