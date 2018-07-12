import scipy.ndimage
from mmappickle import mmapdict
import numpy
from matplotlib import pyplot as plt
import matplotlib as mpl
import hics.utils.datafile
import skimage.segmentation

class AutoMaskAlgorithm:
    def __init__(self, data, maskspec):
        self._data = data

    @property
    def data(self):
        return self._data

    @property
    def data_scalar(self):
        return numpy.log(self._data.mean(2))

    def mpl_init_structures(self, ax):
        self._mpl_mask_im = numpy.zeros(self._data.shape[:2]+(4, ))
        self._mpl_mask_im[:, :, 0] = 1
        self._mpl_mask = ax.imshow(self._mpl_mask_im)

    def mpl_update_plot(self, ax):
        #Update mask (alpha channel)
        self._mpl_mask_im[:, :, 3] = (self.get_mask() == 0) * 0.2
        self._mpl_mask.set_data(self._mpl_mask_im)

    def get_mask(self):
        return numpy.zeros(self._data.shape[:2])

    def mpl_on_motion(self, event):
        pass

    def mpl_on_press(self, event):
        pass

    def mpl_on_release(self, event):
        pass

    def mpl_on_key_press(self, event):
        pass

    def mpl_on_key_release(self, event):
        pass


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
        super().mpl_init_structures(ax)
        self._mpl_maskpoints, = ax.plot([], [], 'o', picker=5)

    def mpl_update_plot(self, ax):
        super().mpl_update_plot(ax)

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
        super().mpl_init_structures(ax)

        self._mpl_maskpoints_in, = ax.plot([], [], 'ob', picker=5)
        self._mpl_maskpoints_out, = ax.plot([], [], 'or', picker=5)

    def mpl_update_plot(self, ax):
        super().mpl_update_plot(ax)

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

class CircularSnakeOptimizer:
    def __init__(self, snake, image):
        self._snake = snake
        self._image = image



class TopoMaskAlgorithm(AutoMaskAlgorithm):
    def __init__(self, data, maskspec):
        super().__init__(data, maskspec)

        self._norm_data = (data - data.mean(2)[:,:,numpy.newaxis]) / data.std(2)[:,:,numpy.newaxis]

        gr = numpy.gradient(self._norm_data, axis=(0, 1))
        gr_n = numpy.sqrt(gr[0]**2+gr[1]**2)
        gr_d = numpy.arctan2(gr[0], gr[1])
        self._gradient_magnitude = numpy.linalg.norm(gr_n, 2, axis=2)

        if maskspec is None:
            self._maskspec = []
        elif type(maskspec) == list:
            if type(maskspec[0]) == str:
                maskspec = [numpy.reshape([float(y) for y in x.split(',')], (-1, 3)) for x in args.maskspec]
                pass
            self._maskspec = maskspec


    def mpl_init_structures(self, ax):
        super().mpl_init_structures(ax)

        self._points_artists = []

        self._cursor = mpl.patches.Circle((10, 10), radius=10, alpha=0.5, color='r')
        ax.add_artist(self._cursor)


    def mpl_update_plot(self, ax):
        super().mpl_update_plot(ax)

        npts = sum([0]+[x.shape[0	] for x in self._maskspec])
        while len(self._points_artists) < npts:
            ptsartist = mpl.patches.Circle((0, 0), radius=0, alpha=0.2, color='g')
            ax.add_artist(ptsartist)
            self._points_artists.append(ptsartist)

        while len(self._points_artists) > npts:
            ax.remove_artist(self._points_artists.pop(-1))

        artidx = 0
        for ms in self._maskspec:
            for p in ms:
                pa = self._points_artists[artidx]
                artidx += 1
                pa.center = p[:2]
                pa.radius = numpy.abs(p[2])
                if pa.radius < 0:
                    pa.set_color('r')
                else:
                    pa.set_color('b')

    def _clear_mask_cache(self):
        self._mask_cache = None

    def get_mask(self):
        if getattr(self, '_mask_cache', None) is not None:
            return self._mask_cache

        global_mask = numpy.zeros(self._data.shape[:2])
        for ms in self._maskspec:
            ms_mask = numpy.zeros(self._data.shape[:2])
            ms_cycled = numpy.concatenate([ms, ms[0:1, :]], 0)
            for p1, p2 in zip(ms_cycled[1:], ms_cycled[:-1]):
                p_mask = numpy.zeros(self._data.shape[:2])
                mg = numpy.array(numpy.meshgrid(numpy.arange(self._data.shape[0]), numpy.arange(self._data.shape[1]), indexing='ij')).astype(numpy.float)

                center = p1[:2][::-1]
                mg1 = mg - numpy.array(center)[:, numpy.newaxis, numpy.newaxis]
                p_mask = numpy.logical_or(p_mask, numpy.sqrt(mg1[0, :, :] ** 2 + mg1[1, :, :] ** 2) <p1[2])

                center = p2[:2][::-1]
                mg2 = mg - numpy.array(center)[:, numpy.newaxis, numpy.newaxis]
                p_mask = numpy.logical_or(p_mask, numpy.sqrt(mg2[0, :, :] ** 2 + mg2[1, :, :] ** 2) <p2[2])

                import skimage, skimage.morphology
                ms_mask = numpy.logical_or(ms_mask, skimage.morphology.convex_hull_image(p_mask))

            if False:
                #Compute active_contour
                contour_image = self.get_mask()*self._gradient_magnitude
                contour_image /= contour_image.max()
                #contour_image = ms_mask*self._gradient_magnitude

                npts = 10

                init = []
                ms = self._maskspec[0]
                ms_cycled = numpy.concatenate([ms, ms[0:1, :]], 0)
                for p1, p2 in zip(ms_cycled[:-1], ms_cycled[1:]):
                    xs = numpy.linspace(p1[0], p2[0], npts)[:-1]
                    ys = numpy.linspace(p1[1], p2[1], npts)[:-1]
                    zs = numpy.linspace(p1[2], p2[2], npts)[:-1]
                    init.append(numpy.concatenate([xs[:, numpy.newaxis], ys[:, numpy.newaxis], zs[:, numpy.newaxis]], 1))

                init = numpy.concatenate(init, 0)

                #CircularSnakeOptimizer(init, contour_image)

                #Random walk
                simul_move = 3
                current_snake = init.copy()
                old_snake_score = 0

                #for i in range(npts*init.shape[0]*10):
                while True:
                    current_snake_cycled = numpy.concatenate([current_snake, current_snake[0:1, ...]], 0)
                    current_snake_score = 0
                    current_snake_dist = 0
                    x_tot = []
                    y_tot = []
                    for p0, p1 in zip(current_snake_cycled[:-1], current_snake_cycled[1:]):
                        x0, y0, z0 = p0
                        x1, y1, z1 = p1

                        current_snake_dist += numpy.linalg.norm(p1[:2]-p0[:2])

                        length = int(numpy.hypot(x1-x0, y1-y0))
                        x, y = numpy.linspace(x0, x1, length), numpy.linspace(y0, y1, length)
                        x_tot.append(x)
                        y_tot.append(y)

                    x_tot = numpy.concatenate(x_tot).astype(numpy.int)
                    y_tot = numpy.concatenate(y_tot).astype(numpy.int)
                    dup_check = list(set([tuple(x) for x in numpy.array([x_tot, y_tot]).T]))
                    x_tot = [x[0] for x in dup_check]
                    y_tot = [x[1] for x in dup_check]
                    path_pixels = contour_image[y_tot, x_tot]
                    if numpy.any(path_pixels<=0):
                        #Invalid pixels?
                        current_snake_score = 0
                    else:
                        current_snake_score += path_pixels.sum()
                        current_snake_score /= (current_snake_dist ** 1.5)
                    # if current_snake_score > 0:
                        # #Remove score depending on the angles
                        # for p0, p1, p2 in zip(current_snake_cycled[:-2], current_snake_cycled[1:-1], current_snake_cycled[2:]):
                            # ba = p1[:2] - p0[:2]
                            # bc = p1[:2] - p2[:2]

                            # cosine_angle = numpy.dot(ba, bc) / (numpy.linalg.norm(ba) * numpy.linalg.norm(bc))
                            # angle = numpy.degrees(numpy.arccos(cosine_angle)) / 180
                            # current_snake_score -= angle

                    if current_snake_score < old_snake_score:
                        current_snake = old_snake.copy()
                        current_snake_score = old_snake_score

                    assert current_snake_score > 0

                    old_snake = current_snake.copy()
                    old_snake_score = current_snake_score

                    initial_position = numpy.random.randint(0, current_snake.shape[0])
                    for p_id in range(simul_move):
                        p_idx = (p_id + initial_position) % current_snake.shape[0]
                        new_pos = numpy.array([-1, -1])
                        while numpy.any(new_pos <0) or numpy.any(new_pos>numpy.array([contour_image.shape[1], contour_image.shape[0]])) or contour_image[new_pos[1], new_pos[0]] <= 0:
                            new_pos = numpy.random.normal(current_snake[p_idx, :2], current_snake[p_idx, 2]/3).astype(numpy.int)
                        current_snake[p_idx, :2] = new_pos


                    print(current_snake_score)

                plt.imshow(contour_image)
                plt.plot(ms[:, 0], ms[:, 1], '--g', lw=3)
                plt.plot(init[:, 0], init[:, 1], '--r', lw=3)
                plt.plot(current_snake[:, 0], current_snake[:, 1], '-+b', lw=3)
                plt.show()

            if ms[0][2] > 0:
                global_mask = numpy.logical_or(global_mask, ms_mask)
            else:
                global_mask = numpy.logical_and(global_mask, ~ms_mask)



        self._mask_cache = global_mask
        return global_mask

    def mpl_on_motion(self, event):
        if event.inaxes is None:
            return
        self._cursor.center = event.xdata, event.ydata
        return True

    def mpl_on_scroll(self, event):
        if event.button == 'up':
            self._cursor.radius += 1
            return True
        else:
            if self._cursor.radius > 1:
                self._cursor.radius -= 1
                return True


    def mpl_on_press(self, event):
        if event.button == 1:
            if len(self._maskspec) == 0:
                self._maskspec.append(numpy.empty((0, 3)))

            self._maskspec[0] = numpy.concatenate([self._maskspec[0], numpy.array([[self._cursor.center[0], self._cursor.center[1], self._cursor.radius]])], 0)

            self._clear_mask_cache()

    def mpl_on_key_press(self, event):
        import IPython
        IPython.embed()


    def mpl_on_release(self, event):
        pass

    def get_maskspec_arg(self):
        return [','.join(str(x) for x in m.flatten()) for m in self._maskspec]

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
        fig.canvas.mpl_connect('scroll_event', self._mpl_on_scroll)
        fig.canvas.mpl_connect('key_press_event', self._mpl_on_key_press)
        fig.canvas.mpl_connect('key_release_event', self._mpl_on_key_release)

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

    def _mpl_on_scroll(self, event):
        if self._automask_algorithm.mpl_on_scroll(event):
            self._mpl_update_plot()

    def _mpl_on_key_press(self, event):
        if self._automask_algorithm.mpl_on_key_press(event):
            self._mpl_update_plot()

    def _mpl_on_key_release(self, event):
        if self._automask_algorithm.mpl_on_key_release(event):
            self._mpl_update_plot()



    def _mpl_update_plot(self):
        self._automask_algorithm.mpl_update_plot(self._mpl_fig.axes[0])
        self._mpl_fig.canvas.toolbar.set_cursor = lambda cursor: None
        self._mpl_fig.canvas.draw_idle()


if __name__ == '__main__':
    import argparse, sys

    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help = 'input file', metavar='file.hdr', required = True)
    parser.add_argument('--output', help = 'output file', metavar='file.mhdr', required=True)
    parser.add_argument('--maskspec', help = 'Mask specification', metavar='maskspec', nargs='+', required=False)
    parser.add_argument('--method', help='Method to use', choices=('click', 'clickdrag', 'topo'), default='click')
    parser.add_argument('--nocrop', help = 'Do not crop output', action='store_true')
    parser.add_argument('--edit', help = 'Force edit', action='store_true')

    args = parser.parse_args()

    input_data = mmapdict(args.input, True)

    if args.method == 'click':
        algo = NearestMaskAlgorithm(input_data['hdr'], args.maskspec)
    elif args.method == 'clickdrag':
        algo = SimplyConnectedDistanceAutoMaskAlgorithm(input_data['hdr'], args.maskspec)
    elif args.method == 'topo':
        algo = TopoMaskAlgorithm(input_data['hdr'], args.maskspec)



    if args.maskspec is None or args.edit:
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
