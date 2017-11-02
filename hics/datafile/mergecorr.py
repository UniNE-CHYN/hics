from mmappickle import mmapdict
from mmappickle.stubs import EmptyNDArray
import pickle
import numpy
import scipy.stats
import re
import skimage.feature
import skimage.transform
import itertools
import functools

class HDRMakerCorr:
    patch_size = numpy.array([50, 50]) #should be divisible by 2 in each dimension
    patch_positions = (1/6, 1/2, 5/6)
    
    def __init__(self, input_data, output_data):
        self._input_data = input_data
        self._output_data = output_data
        self._im_ids = sorted([int(x[5:]) for x in input_data.keys() if x.startswith('refl-') and x[5:].isnumeric()])
        
    @property
    def im_ids(self):
        return list(self._im_ids)
    
    def get_im(self, im_id):
        return self._input_data['refl-{0:05d}'.format(im_id)][:, :, 64]

    def get_patches_for(self, im_id):
        ckey = 'patches-{0:05d}'.format(im_id)
        if ckey not in self._output_data.keys():
            srcim = self.get_im(im_id)
            #Generate patches
            patches = {}
            for flip_y in [True,False]:
                for flip_x in [True,False]:
                    patches[flip_y, flip_x] = []
                    srcim_flipped = srcim[::{True:-1,False:1}[flip_y],::{True:-1,False:1}[flip_x]]
                    
                    for ppyp in self.patch_positions:
                        ppy = min(max(0, int(ppyp * srcim.shape[0] - self.patch_size[0] / 2)), srcim.shape[0] - self.patch_size[0])
                        for ppxp in self.patch_positions:
                            ppx = min(max(0, int(ppxp * srcim.shape[1] - self.patch_size[1] / 2)), srcim.shape[1] - self.patch_size[1])
                            
                            patch = numpy.copy(srcim_flipped[ppy:ppy+self.patch_size[0],ppx:ppx+self.patch_size[1]])
                            patch -= patch.mean()
                            assert patch.shape== tuple(self.patch_size)
                            
                            patches[flip_y, flip_x].append((patch, (ppy, ppx)))
                            
            self._output_data[ckey] = patches
        return self._output_data[ckey]
    
    def get_pos_and_score(self, im_id, match_on_im, flip_y, flip_x):
        ckey = 'match-{:05d}-{:05d}-{}-{}'.format(im_id, match_on_im, {True: 1, False: 0}[flip_y], {True: 1, False: 0}[flip_x])
        if ckey not in self._output_data.keys():        
            srcim = self.get_im(im_id)
            dstim = self.get_im(match_on_im)
            target = numpy.copy(dstim)
            target -= target.mean()
            corr_im = numpy.zeros(numpy.array(srcim.shape)+numpy.array(dstim.shape))
            for patch, pos in self.get_patches_for(im_id)[flip_y, flip_x]:
                corr = scipy.signal.correlate2d(target, patch, boundary='symm', mode='same')
                corr_im[srcim.shape[0] - pos[0]:srcim.shape[0] - pos[0] +corr.shape[0], srcim.shape[1] - pos[1]:srcim.shape[1] - pos[1] +corr.shape[1]] += corr
            
            corr_pos = numpy.array(numpy.unravel_index(numpy.argmax(corr_im), corr_im.shape)) - self.patch_size//2 + numpy.array([1, 1])
            
            dstim_padded = numpy.ones(2*numpy.array(srcim.shape)+numpy.array(dstim.shape))*numpy.nan
            dstim_padded[srcim.shape[0]:srcim.shape[0]+dstim.shape[0], srcim.shape[1]:srcim.shape[1]+dstim.shape[1]] = dstim
            
            srcim_padded = numpy.ones(2*numpy.array(srcim.shape)+numpy.array(dstim.shape))*numpy.nan
            srcim_padded[corr_pos[0]:corr_pos[0]+srcim.shape[0], corr_pos[1]:corr_pos[1]+srcim.shape[1]] = srcim[::{True:-1,False:1}[flip_y],::{True:-1,False:1}[flip_x]]
            
            delta = numpy.ma.masked_invalid(dstim_padded - srcim_padded)
            corr_pos_rel = corr_pos - numpy.array(srcim.shape)
            corr_score = numpy.abs(delta).sum() / (~delta.mask).sum()
            self._output_data[ckey] = corr_pos_rel, corr_score
        return self._output_data[ckey]
    
def job_get_patches_for(a):
    im_i, input_data, output_data = a
    hdr = HDRMakerCorr(input_data, output_data)
    hdr.get_patches_for(im_i)
    
def job_match(a):
    im_i, im_j, flip_x, flip_y, input_data, output_data = a
    hdr = HDRMakerCorr(input_data, output_data)
    pos, score = hdr.get_pos_and_score(im_i, im_j, flip_x=flip_x, flip_y=flip_y)
    print(im_i, im_j, 'Xf:', {True: 1, False: 0}[flip_x], 'Yf:', {True: 1, False: 0}[flip_y], pos, score)
    return pos, score

if __name__ == '__main__':
    import argparse
    import hics.utils.datafile
    import multiprocessing
    
    parser = argparse.ArgumentParser()    
    parser.add_argument('--input', help = 'input file (reflectance file)', required = True)
    parser.add_argument('--output', help = 'output file (hdr file)', required=True)
    parser.add_argument('--clean', help = 'leave only hdr data in output file', action='store_true')
    parser.add_argument('--parallel', type=int, required=False)
    
    args = parser.parse_args()
    
    input_data, output_data =  hics.utils.datafile.migrate_base_data(args, 'hics.datafile.mergecorr')
    
    hdr = HDRMakerCorr(input_data, output_data)
    
    #Match images (CPU intensive)
    parameters_to_compute = list(itertools.product(hdr.im_ids, hdr.im_ids, [True, False], [True, False], [input_data], [output_data]))
    
    numcpus = hics.utils.datafile.get_cpu_count(args)
    
    
    
    if numcpus == 1:
        for a in parameters_to_compute:
            job_match(a)
    else:
        with multiprocessing.Pool(numcpus) as p:
            for k in p.imap_unordered(job_get_patches_for, itertools.product(hdr.im_ids, [input_data], [output_data])):
                pass                
            for k in p.imap_unordered(job_match, parameters_to_compute):
                pass
            
    possibilities = list(itertools.product(hdr.im_ids, hdr.im_ids, [True, False], [True, False]))
    score_matrix = numpy.zeros((len(possibilities), 7))
    for p_id, a in enumerate(possibilities):
        im_i, im_j, flip_y, flip_x = a
        pos, score = hdr.get_pos_and_score(im_i, im_j, flip_x=flip_x, flip_y=flip_y)
        score_matrix[p_id][0] = im_i
        score_matrix[p_id][1] = im_j
        score_matrix[p_id][2] = flip_y
        score_matrix[p_id][3] = flip_x
        score_matrix[p_id][4] = score
        score_matrix[p_id][5] = pos[0]
        score_matrix[p_id][6] = pos[1]
        
    #Sort by 4-th column
    score_matrix = score_matrix[score_matrix[:, 4].argsort()]
    #remove images which are matched to themselves
    score_matrix = score_matrix[score_matrix[:, 0]!=score_matrix[:, 1]]
    
    #Greedy reconstruct
    #(im_id, pos_y, pos_x, flip_y, flip_x)
    images = [(int(score_matrix[0][1]), 0, 0, 0, 0)]
    
    im_shapes = dict([(k, hdr.get_im(k).shape) for k in hdr.im_ids])
    
    def make_mask(im):
        def make_mask_vec(l):
            hmv = numpy.linspace(0, 1, int(numpy.ceil(l/2)) + 1)
            if l % 2 == 1:
                return numpy.concatenate([hmv[1:-1], hmv[1:][::-1]])
            else:
                return numpy.concatenate([hmv[1:], hmv[1:][::-1]])
            
        vm = make_mask_vec(im.shape[0])[:, numpy.newaxis]
        hm = make_mask_vec(im.shape[1])[numpy.newaxis, :]
        return vm * hm
        
            
    
    def blit_images(im_list):
        im_dict = {}
        min_pos_y = 0
        max_pos_y = 0
        min_pos_x = 0
        max_pos_x = 0        
        for im_list_entry in im_list:
            im_id, pos_y, pos_x, flip_y, flip_x = im_list_entry
            im_dict[im_id] = hdr.get_im(im_id)
            min_pos_y = min(pos_y, min_pos_y)
            min_pos_x = min(pos_x, min_pos_x)
            max_pos_y = max(pos_y+im_dict[im_id].shape[0], max_pos_y)
            max_pos_x = max(pos_x+im_dict[im_id].shape[1], max_pos_x)
            
        target = numpy.ma.zeros((max_pos_y-min_pos_y, max_pos_x-min_pos_x))
        target_coeff = numpy.ma.zeros((max_pos_y-min_pos_y, max_pos_x-min_pos_x))
        for im_list_entry in im_list:
            im_id, pos_y, pos_x, flip_y, flip_x = im_list_entry
            im = im_dict[im_id]
            coeff_matrix = make_mask(im)  #numpy.ones_like(im)   #FIXME: improve this!
            target[pos_y-min_pos_y:pos_y-min_pos_y+im.shape[0], pos_x-min_pos_x:pos_x-min_pos_x+im.shape[1]] += im[::{1:-1,0:1}[flip_y],::{1:-1,0:1}[flip_x]] * coeff_matrix
            target_coeff[pos_y-min_pos_y:pos_y-min_pos_y+im.shape[0], pos_x-min_pos_x:pos_x-min_pos_x+im.shape[1]] += coeff_matrix
            
        return numpy.ma.masked_invalid(target / target_coeff)
        

    while any([x not in [y[0] for y in images] for x in hdr.im_ids]):
        found = False
        for score_im_i, score_im_j, score_flip_y, score_flip_x, score_score, score_pos_y, score_pos_x in score_matrix:
            #Image already seen
            if int(score_im_i) in [y[0] for y in images]:
                continue
            for cur_im_id, cur_pos_y, cur_pos_x, cur_flip_y, cur_flip_x in images:
                if int(score_im_j) == cur_im_id:
                    found = True
                    new_im_id = int(score_im_i)
                    if not cur_flip_x:
                        new_pos_x = cur_pos_x + score_pos_x
                    else:
                        new_pos_x = cur_pos_x + im_shapes[cur_im_id][1] - score_pos_x - im_shapes[score_im_j][1]
                    if not cur_flip_y:
                        new_pos_y = cur_pos_y + score_pos_y
                    else:
                        new_pos_y = cur_pos_y + im_shapes[cur_im_id][0] - score_pos_y - im_shapes[score_im_j][0]
                        
                    new_flip_x = cur_flip_x ^ int(score_flip_x)
                    new_flip_y = cur_flip_y ^ int(score_flip_y)
                    
                    images.append((new_im_id, int(new_pos_y), int(new_pos_x), new_flip_y, new_flip_x))
                    break
            if found:
                break
                    
        if not found:
            break
        
    im = blit_images(images)
    from matplotlib import pyplot as plt
    plt.imshow(im)
    plt.clim(0, 1)
    plt.colorbar()
    plt.show()
    import IPython
    IPython.embed()
