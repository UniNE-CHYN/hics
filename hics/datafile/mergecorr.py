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
    sys.exit(0)
    
import numpy
import skimage.transform
import IPython
from matplotlib import pyplot as plt
from mmappickle import mmapdict
import scipy.signal
#srcpoints=numpy.load('src.npy')
#dstpoints=numpy.load('dst.npy')

#IPython.embed()
#(dstpoints, srcpoints)
#skimage.transform.AffineTransform
d = mmapdict('../unige/ER-146-F.calibrated',True)
srcim = d['refl-00000'][:,:,64] #[:,::-1] #move
dstim = d['refl-00001'][:,:,64] #Doesn't move

self.patch_size = numpy.array([50, 50]) #should be divisible by 2 in each dimension
patch_positions = (1/6, 1/2, 5/6)



#Generate patches
patches = {}
for flip_y in [True,False]:
    for flip_x in [True,False]:
        patches[flip_y, flip_x] = []
        srcim_flipped = srcim[::{True:-1,False:1}[flip_y],::{True:-1,False:1}[flip_x]]
        
        for ppyp in patch_positions:
            ppy = min(max(0, int(ppyp * srcim.shape[0] - self.patch_size[0] / 2)), srcim.shape[0] - self.patch_size[0])
            for ppxp in patch_positions:
                ppx = min(max(0, int(ppxp * srcim.shape[1] - self.patch_size[1] / 2)), srcim.shape[1] - self.patch_size[1])
                
                patch = numpy.copy(srcim_flipped[ppy:ppy+self.patch_size[0],ppx:ppx+self.patch_size[1]])
                patch -= patch.mean()
                assert patch.shape==self.patch_size
                
                patches[flip_y, flip_x].append((patch, (ppy, ppx)))
                
                
flip_y, flip_x = False, False

target = numpy.copy(dstim)
target -= target.mean()
corr_im = numpy.zeros(numpy.array(srcim.shape)+numpy.array(dstim.shape))
for patch, pos in patches[flip_y, flip_x]:
    print(pos)
    corr = scipy.signal.correlate2d(target, patch, boundary='symm', mode='same')
    corr_im[srcim.shape[0] - pos[0]:srcim.shape[0] - pos[0] +corr.shape[0], srcim.shape[1] - pos[1]:srcim.shape[1] - pos[1] +corr.shape[1]] += corr

corr_pos = numpy.array(numpy.unravel_index(numpy.argmax(corr_im), corr_im.shape)) - self.patch_size//2

#Evaluate score
#Get intersection image

dstim_padded = numpy.ones(2*numpy.array(srcim.shape)+numpy.array(dstim.shape))*numpy.nan
dstim_padded[srcim.shape[0]:srcim.shape[0]+dstim.shape[0], srcim.shape[1]:srcim.shape[1]+dstim.shape[1]] = dstim

srcim_padded = numpy.ones(2*numpy.array(srcim.shape)+numpy.array(dstim.shape))*numpy.nan
srcim_padded[corr_pos[0]:corr_pos[0]+srcim.shape[0], corr_pos[1]:corr_pos[1]+srcim.shape[1]] = srcim[::{True:-1,False:1}[flip_y],::{True:-1,False:1}[flip_x]]

delta = numpy.ma.masked_invalid(dstim_padded - srcim_padded)
print(numpy.abs(delta).sum() / (~delta.mask).sum())


plt.imshow(numpy.ma.masked_invalid(dstim_padded - srcim_padded))
plt.show()
