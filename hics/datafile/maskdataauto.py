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
    _distance_exponent = 1.1
    _pixel_exponent = 1.5

    def __init__(self, snake, image, snake_interpolate=10):

        init = []
        ms = snake
        ms_cycled = numpy.concatenate([ms, ms[0:1, :]], 0)
        for p1, p2 in zip(ms_cycled[:-1], ms_cycled[1:]):
            xs = numpy.linspace(p1[0], p2[0], snake_interpolate)[:-1]
            ys = numpy.linspace(p1[1], p2[1], snake_interpolate)[:-1]
            zs = numpy.linspace(p1[2], p2[2], snake_interpolate)[:-1]
            init.append(numpy.concatenate([xs[:, numpy.newaxis], ys[:, numpy.newaxis], zs[:, numpy.newaxis]], 1))

        init = numpy.concatenate(init, 0)


        self._snake_init = init.copy()
        self._snake = init.copy()
        self._image = image

    @property
    def score(self):
        return self.score_for_snake(self._snake)

    @property
    def distance(self):
        return self.distance_for_snake(self._snake)

    @property
    def fitness(self):
        return self.fitness_for_score_and_distance(self.score, self.distance)


    def fitness_for_score_and_distance(self, score, distance):
        return score / (distance ** self._distance_exponent)

    @staticmethod
    def cycled(d):
        return numpy.concatenate([d, d[0:1, ...]], 0)

    def distance_for_snake(self, snake, cycled=True):
        if cycled:
            snake_cycled = CircularSnakeOptimizer.cycled(snake)
        else:
            snake_cycled = snake
        dist = 0
        for p0, p1 in zip(snake_cycled[:-1], snake_cycled[1:]):
            dist += numpy.linalg.norm(p1[:2]-p0[:2])
        return dist

    def score_for_snake(self, current_snake, cycled=True):
        if cycled:
            current_snake_cycled = CircularSnakeOptimizer.cycled(current_snake)
        else:
            current_snake_cycled = current_snake

        score = 0
        for p0, p1 in zip(current_snake_cycled[:-1], current_snake_cycled[1:]):
            x0, y0, z0 = p0
            x1, y1, z1 = p1

            length = int(numpy.hypot(x1-x0, y1-y0))
            x, y = numpy.linspace(x0, x1, length), numpy.linspace(y0, y1, length)
            pixels = self._image[y.astype(numpy.int), x.astype(numpy.int)]
            if numpy.any(pixels<=0):
                return 0

            score += (pixels ** self._pixel_exponent).sum()
        return score

    def optimize(self, steps, simul_move=3, random_ratio=0.5):
        distance = self.distance_for_snake(self._snake)
        score = self.score_for_snake(self._snake)
        fitness = self.fitness_for_score_and_distance(score, distance)

        for step_id in range(steps):

            initial_position = numpy.random.randint(0, self._snake.shape[0])
            old_snake_part = []
            new_snake_part = []
            for p_id in range(simul_move+2):
                p_idx = (p_id + initial_position) % self._snake.shape[0]
                old_snake_part.append(self._snake[p_idx, :])

                #Don't move the ends
                if p_id == 0 or p_id == simul_move + 1:
                    new_snake_part.append(self._snake[p_idx, :])
                else:
                    new_pos = numpy.array([-1, -1])
                    while numpy.any(new_pos <0) or \
                          numpy.any(new_pos>numpy.array([self._image.shape[1], self._image.shape[0]])) or \
                          self._image[new_pos[1], new_pos[0]] <= 0:
                        new_pos = numpy.random.normal(self._snake[p_idx, :2], self._snake[p_idx, 2]*random_ratio).astype(numpy.int)

                    new_snake_part.append(numpy.array([new_pos[0], new_pos[1], self._snake[p_idx, 2]]))

            new_distance = distance - self.distance_for_snake(old_snake_part, cycled=False) + self.distance_for_snake(new_snake_part, cycled=False)
            new_snake_part_score = self.score_for_snake(new_snake_part, cycled=False)
            if new_snake_part_score == 0:
                new_score = 0
            else:
                new_score = score - self.score_for_snake(old_snake_part, cycled=False) + new_snake_part_score
            new_fitness = self.fitness_for_score_and_distance(new_score, new_distance)

            if False:
                #Checks
                new_snake = self._snake.copy()
                for p_id, new_p in enumerate(new_snake_part):
                    p_idx = (p_id + initial_position) % self._snake.shape[0]
                    new_snake[p_idx, :] = new_p

                assert numpy.abs(self.distance_for_snake(new_snake) - new_distance) < 0.01
                assert numpy.abs(self.score_for_snake(new_snake) - new_score) < 0.01

                print(fitness, new_fitness, new_distance, new_score)
            if new_fitness > fitness:
                for p_id, new_p in enumerate(new_snake_part):
                    p_idx = (p_id + initial_position) % self._snake.shape[0]
                    self._snake[p_idx, :] = new_p

                distance = new_distance
                score = new_score
                fitness = new_fitness

class CircularAntSystemOptimizer:
    _distance_exponent = 1.1
    _pixel_exponent = 1.5

    _candidate_positions_delta = numpy.array([
        [1, 0],
        [1, 1],
        [0, 1],
        [-1, 1],
        [-1, 0],
        [-1, -1],
        [0, -1],
        [1, -1],
    ])

    _preferred_direction_factor = 0.00

    def __init__(self, ref_positions, image):
        self._ref_positions = ref_positions.copy()
        ref_positions_c = numpy.concatenate([self._ref_positions, self._ref_positions[0:1, ...]], 0)
        self._ref_positions_middles = (ref_positions_c[:-1] + ref_positions_c[1:]) / 2
        self._image = image
        self._pheromone = numpy.zeros_like(self._image)
        #y,x
        self._valid_pixels = numpy.array(numpy.nonzero(self._image)).T

        init = []
        ref_positions_cycled = numpy.concatenate([ref_positions, ref_positions[0:1, :]], 0)
        for p1, p2 in zip(ref_positions_cycled[:-1], ref_positions_cycled[1:]):
            xs = numpy.linspace(p1[0], p2[0], 20)[:-1]
            ys = numpy.linspace(p1[1], p2[1], 20)[:-1]
            z1s = numpy.ones_like(xs) * (p2[1] - p1[1])
            z2s = numpy.ones_like(xs) * (p2[0] - p1[0])
            init.append(numpy.concatenate([xs[:, numpy.newaxis], ys[:, numpy.newaxis], z1s[:, numpy.newaxis], z2s[:, numpy.newaxis]], 1))

        init = numpy.concatenate(init, 0)

        self._preferred_direction = numpy.zeros(self._image.shape+(8, )) * numpy.nan
        cpd_norm = self._candidate_positions_delta / numpy.linalg.norm(self._candidate_positions_delta, axis=1)[:, numpy.newaxis]
        for px in self._valid_pixels:
            deltas = init[:,1:None:-1]-px
            nearest = init[numpy.argmin(numpy.linalg.norm(deltas, axis=1))][2:]
            nearest_norm =  nearest / numpy.linalg.norm(nearest)


            self._preferred_direction[px[0], px[1]] = cpd_norm.dot(nearest_norm)

        self.optimize(200, 100)
        print(cpd_norm)

    def optimize(self, n_ants, path_length):
        ants_positions = numpy.zeros((n_ants, path_length, 2), dtype=numpy.int)
        ants_positions[:, 0, :] = self._valid_pixels[numpy.random.choice(self._valid_pixels.shape[0],n_ants)]



        for step_id in range(1, path_length):
            for ant_positions in ants_positions:
                current_position = ant_positions[step_id-1]
                candidate_positions = current_position + self._candidate_positions_delta
                scores = self._preferred_direction_factor * self._preferred_direction[current_position[0], current_position[1]]
                #Better way?
                invalid = numpy.zeros(len(self._candidate_positions_delta), dtype=numpy.bool)
                for cpi, candidate_position in enumerate(candidate_positions):
                    if not all(candidate_position < self._pheromone.shape) or not all(candidate_position>0):
                        invalid[cpi] = True
                    elif self._image[candidate_position[0], candidate_position[1]] == 0:
                        #Border => all invalid!!!
                        invalid[:] = True
                    elif candidate_position in ant_positions[:step_id-1]:
                        invalid[cpi] = True
                    else:
                        scores[cpi] += self._pheromone[candidate_position[0], candidate_position[1]]

                scores -= scores.min()
                scores[invalid] = 0
                if numpy.all(invalid):
                    ant_positions[step_id] = current_position
                else:
                    if scores.sum() == 0:
                        scores[:] = 1
                    scores /= scores.sum()
                    assert not numpy.any(numpy.isnan(scores))
                    ant_positions[step_id] = candidate_positions[numpy.random.choice(numpy.arange(8), p=scores)]

        new_pheromone = numpy.zeros_like(self._pheromone)
        for ant_id in range(n_ants):
            idxs = numpy.ravel_multi_index(ants_positions[ant_id].T, self._image.shape)
            score = self._image.ravel()[idxs].sum() / len(set(idxs))
            #FIXME: should not happen
            if not numpy.isnan(score) and len(set(idxs)) > 5:
                new_pheromone.ravel()[idxs] += score

        new_pheromone /= new_pheromone.max()

        self._pheromone = 0.6 * self._pheromone + new_pheromone
        plt.imshow(self._pheromone)
        plt.draw()
        #plt.plot(ant_positions)


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

        self._cso_orig, = plt.plot([], [], '--r', lw=3)
        self._cso_opt, = plt.plot([], [], '-+b', lw=3)

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

            if ms[0][2] > 0:
                global_mask = numpy.logical_or(global_mask, ms_mask)
            else:
                global_mask = numpy.logical_and(global_mask, ~ms_mask)

        contour_image = global_mask*self._gradient_magnitude
        contour_image /= contour_image.max()
        self.caso = CircularAntSystemOptimizer(self._maskspec[0], contour_image)

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

        contour_image = self.get_mask()*self._gradient_magnitude
        contour_image /= contour_image.max()

        if getattr(self, 'caso', None) is None:
            #self.cso = CircularSnakeOptimizer(self._maskspec[0], contour_image)
            self.caso = CircularAntSystemOptimizer(self._maskspec[0], contour_image)
        #self.cso.optimize(4000, 3, 0.2)
        self.caso.optimize(n_ants=1000, path_length=100)

        if True:
            self._cso_orig.set_data(self.cso._snake_init[:, 0], self.cso._snake_init[:, 1])
            self._cso_opt.set_data(self.cso._snake[:, 0], self.cso._snake[:, 1])
            plt.draw()


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
