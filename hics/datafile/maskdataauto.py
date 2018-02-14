import scipy.ndimage
from mmappickle import mmapdict
import numpy
from matplotlib import pyplot as plt
import hics.utils.datafile

class Automask:
    def __init__(self, data, maskspec):
        self._data = data
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
        
        self._mpl_ignore_press = False
        
    def _mpl_on_pick(self, event):
        self._current_point_id = None
        
        if event.artist != self._mpl_maskpoints:
            return True
        for point_id in sorted(event.ind, reverse=True):
            self._maskspec.pop(point_id)
            self._cache_score.pop(point_id)
            
        self._mpl_update_plot()
        self._mpl_ignore_press = True
        return True
        
    def _mpl_on_press(self, event):
        if self._mpl_ignore_press:
            self._mpl_ignore_press = False
            return True
        
        self._current_point_id = None
        
        xp = int(event.xdata)
        yp = int(event.ydata)
        if xp < 0 or xp >= self._data.shape[1]:
            return True
        if yp < 0 or yp >= self._data.shape[0]:
            return True
        
        self._maskspec.append([xp, yp, 1])
        self._current_point_id = len(self._maskspec) - 1
        self._mpl_update_plot()
        
    def _mpl_on_release(self, event):
        self._current_point_id = None
        
    def _mpl_on_motion(self, event):
        if self._current_point_id is None:
            return True
        
        xp, yp, sc = self._maskspec[self._current_point_id]
        
        delta = numpy.linalg.norm(numpy.array([event.xdata-xp, event.ydata-yp]))
        new_sc = 1 - numpy.clip(2*delta/min([self._data.shape[0], self._data.shape[1]]), 0, 1)
        self._maskspec[self._current_point_id][2] = round(new_sc, 2)
        
        self._mpl_update_plot()
        
    def get_maskspec_arg(self):
        return ['{},{},{}'.format(x, y, z) for x, y, z in self._maskspec]
        
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
        return scipy.ndimage.binary_fill_holes(mask>0)
        
    def _mpl_update_plot(self):        
        mask_im = numpy.zeros(self._data.shape[:2]+(4, ))
        mask_im[:, :, 3] = (self.get_mask() == 0) * 0.2
        mask_im[:, :, 0] = 1
        
        self._mpl_mask.set_data(mask_im)
        self._mpl_maskpoints.set_data([x[0] for x in self._maskspec], [x[1] for x in self._maskspec])
        self._mpl_fig.canvas.draw()
        
    def interactive_plot(self):
        import numpy as np
        import matplotlib.pyplot as plt
        
        X = np.random.rand(100, 1000) * 100
        xs = np.mean(X, axis=1)
        ys = np.std(X, axis=1)
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title('click and drag to add region to mask')
        
        #Draw the figure!
        meandata = numpy.log(self._data.mean(2))
        ax.imshow(meandata, cmap='gray', clim=(numpy.percentile(meandata.flatten(), 1), numpy.percentile(meandata.flatten(), 99)))
        
        self._mpl_mask = ax.imshow(numpy.zeros(meandata.shape+(4, )))
        self._mpl_maskpoints, = ax.plot([], [], 'o', picker=5)
        
        fig.canvas.mpl_connect('pick_event', self._mpl_on_pick)
        fig.canvas.mpl_connect('button_press_event', self._mpl_on_press)
        fig.canvas.mpl_connect('button_release_event', self._mpl_on_release)
        fig.canvas.mpl_connect('motion_notify_event', self._mpl_on_motion) 
        
        self._mpl_fig = fig
        self._mpl_update_plot()
        
        plt.show()    

if __name__ == '__main__':
    import argparse, sys
    
    parser = argparse.ArgumentParser()    
    parser.add_argument('--input', help = 'input file', metavar='file.hdr', required = True)
    parser.add_argument('--output', help = 'output file', metavar='file.mhdr', required=True)
    parser.add_argument('--maskspec', help = 'Mask specification', metavar='maskspec', nargs='+', required=False)
    
    args = parser.parse_args()
    
    input_data = mmapdict(args.input, True)
    am = Automask(input_data['hdr'], args.maskspec)
   
    if args.maskspec is None:
        #Run in interactive mode...
        am.interactive_plot()
        
    args.maskspec = am.get_maskspec_arg()

    input_data, output_data =  hics.utils.datafile.migrate_base_data(args, 'hics.datafile.maskdataauto')
        
    mask = ~am.get_mask()
    cols = numpy.nonzero(mask.sum(0) != mask.shape[0])[0]
    rows = numpy.nonzero(mask.sum(1) != mask.shape[1])[0]
    
    for k in ('hdr', 'hdr-var'):
        if k in input_data.keys():
            data = numpy.ma.masked_invalid(input_data[k].copy())
            if hasattr(data, "mask"):
                data.mask = numpy.logical_or(data.mask, mask[:, :, numpy.newaxis].repeat(data.mask.shape[2], 2))
            #Crop, check if correct
            data = data[rows.min():rows.max()+1, cols.min():cols.max()+1]
            output_data[k] = data
            
    output_data.vacuum()
