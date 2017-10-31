from mmappickle import mmapdict
from mmappickle.stubs import EmptyNDArray
import pickle
import numpy
import scipy.stats
import re
import skimage.feature
import itertools
import functools

class PolyTF(skimage.transform.SimilarityTransform):
    min_samples = 100
    
    def estimate(*data):
        return skimage.transform.SimilarityTransform.estimate(*data)
        
    def is_model_valid(model, *data):
        return True
        return numpy.abs(numpy.linalg.det(model.params[:, 1:3]) - 1) < 1e-3

class HDRMaker:
    _wldetrsh = 30
    
    def __init__(self, input_data, output_data):
        self._input_data = input_data
        self._output_data = output_data
        self._im_ids = sorted([int(x[5:]) for x in input_data.keys() if x.startswith('refl-') and x[5:].isnumeric()])
        
    def make(self):
        for k in ['description', 'wavelengths', 'white-p']:
            output_data[k] = input_data[k]
            
            
    def get_descriptors(self, im_id):
        descriptor_key = 'descr-{0:05d}'.format(im_id)
        if descriptor_key not in self._output_data:
            print("Detecting ORB keypoints for image {}".format(im_id))
            data = self._input_data['refl-{:05d}'.format(im_id)]
        
            #FIXME: improve wl choice
            wavelengths = list(range(0, data.shape[2], 16))
            
            kp = {}
            descr = {}
            for wl in wavelengths:
                detector = skimage.feature.ORB(n_keypoints=1000, fast_threshold = 0.01)
                try:
                    detector.detect_and_extract(data[:,:,wl])
                    kp[wl] = detector.keypoints
                    descr[wl] = detector.descriptors
                except Exception as e:
                    #print(wl, e)
                    pass
                
            self._output_data[descriptor_key] = (kp, descr)
        return self._output_data[descriptor_key]
    
    def get_match(self, im_i, im_j):
        if im_j < im_i:
            im_i, im_j = im_j, im_i
            reverse = True
        else:
            reverse = False
            
        match_key = 'match-{:05d}-{:05d}'.format(im_i, im_j)
        if match_key not in self._output_data:
            kp_my, de_my = self.get_descriptors(im_i)
            kp_other, de_other = self.get_descriptors(im_j)
            
            print("Matching images {} and {}".format(im_i, im_j))
        
            wavelengths = list(sorted(set(de_my.keys()).intersection(de_other.keys())))
            wavelengths = [wl for wl in wavelengths if len(de_my[wl]) > self._wldetrsh and  len(de_other[wl]) > self._wldetrsh]
            
            self._output_data[match_key] = dict((wl, skimage.feature.match_descriptors(de_my[wl], de_other[wl], cross_check=True)) for wl in wavelengths)
            
        if reverse:
            return dict((wl, v[:, [1, 0]]) for wl, v in self._output_data[match_key].items())
        else:
            return self._output_data[match_key]
        
    def get_match_score(self, im_i, im_j):
        d = self.get_match(im_i, im_j)
    
        return sum([len(d[wl]) for wl in d.keys()])        
        
    @property
    def match_matrix(self):
        k = 'match_matrix'
        if k not in self._output_data.keys():        
            max_im_id = max(self._im_ids) + 1
            mq = numpy.zeros((max_im_id, max_im_id))
            
            for i in sorted(self._im_ids):
                for j in sorted(self._im_ids):
                    m = self.get_match_score(i, j)
                    mq[i,j] = m
            self._output_data[k] = mq
        return self._output_data[k]
        
    @property
    def center_id(self):
        k = 'center_id'
        if k not in self._output_data.keys():
            import scipy.sparse
            m = self.match_matrix
            dgraph = scipy.sparse.csr_matrix(-(m - numpy.diag(numpy.diag(m))))
            mst = scipy.sparse.csgraph.minimum_spanning_tree(dgraph)
            connectedgraph = (mst != 0)
            dist = scipy.sparse.csgraph.dijkstra(connectedgraph + connectedgraph.T, directed = False)
            self._output_data[k] = dist.max(0).argmin()
            
        return self._output_data[k]
    
    def estimate_transform_to(self, im_i, im_j):
        k = 'transform-{:05d}-{:05d}'.format(im_i, im_j)
        if k not in self._output_data.keys():
            kp_my, de_my = self.get_descriptors(im_i)
            kp_other, de_other = self.get_descriptors(im_j)
            
            matches = self.get_match(im_i, im_j)
            
            src = []
            dst = []
            for wl, wlm in matches.items():
                for idx1, idx2 in wlm:
                    src.append([kp_my[wl][idx1][0], kp_my[wl][idx1][1], wl])
                    dst.append([kp_other[wl][idx2][0], kp_other[wl][idx2][1], wl])
        
            src = numpy.array(src)
            dst = numpy.array(dst)
            
            if im_i == im_j:
                #Same image, simple "do-nothing" transform
                self._output_data[k] = skimage.transform.AffineTransform(), src.shape[0], src.shape[0]
            elif len(src) == 0 or len(dst) == 0:
                self._output_data[k] = None, 0, 0
            else:
                #transform, inliers = skimage.measure.ransac((dst[:,:2], src[:,:2]), PolyTF, min_samples=PolyTF.min_samples, is_model_valid = functools.partial(PolyTF.is_model_valid), residual_threshold=1, max_trials=2000)
                wl_fp_count = {}
                for x in itertools.chain(dst[:, -1], src[:, -1]):
                    wl_fp_count[x] = wl_fp_count.get(x, 0) + 1
                wl_fp_count = list(sorted(wl_fp_count.items(), key=lambda x: x[1], reverse=True))
                
                transform, inliers = skimage.measure.ransac((dst[dst[:, -1] == wl_fp_count[0][0]][:,:2], src[src[:, -1] == wl_fp_count[0][0]][:,:2]), PolyTF, min_samples=5, is_model_valid = functools.partial(PolyTF.is_model_valid), residual_threshold=1, max_trials=2000)
                
                if inliers is None:
                    self._output_data[k] = None, None, None
                else:
                    self._output_data[k] = transform, numpy.count_nonzero(inliers), len(inliers)
        return self._output_data[k]
    
    def get_transformed_image(self, im_id):
        k_data = 'transformed-{:05d}'.format(im_id)
        k_mask = 'transformed-{:05d}-mask'.format(im_id)
        k_var = 'transformed-{:05d}-var'.format(im_id)
        if (k_data not in self._output_data.keys() or \
            k_mask not in self._output_data.keys() or \
            k_var not in self._output_data.keys()):
            print("C", im_id)
            import skimage.transform
            #tf = self.estimate_transform_to(im_id, self.center_id)[0]
            tf = self.estimate_transform_to(im_id, self.center_id)[0]
            if tf is None:
                self._output_data[k_data] = None
                self._output_data[k_mask] = None
                self._output_data[k_var] = None
            else:
                #Apply transform
                im = self._input_data['refl-{:05d}'.format(im_id)]
                im_var = self._input_data['refl-{:05d}-var'.format(im_id)]
                
                self._output_data[k_data] = numpy.rollaxis(skimage.transform.warp(numpy.rollaxis(im,1,0), tf, clip = False),1,0)
                self._output_data[k_mask] = 1. - numpy.rollaxis(skimage.transform.warp(numpy.rollaxis(1.-im.mask,1,0), tf, clip = False),1,0)
                mask = numpy.array(self._output_data[k_mask], dtype=numpy.bool)
                self._output_data[k_data][mask] = 0
                self._output_data[k_var] = numpy.rollaxis(skimage.transform.warp(numpy.rollaxis(im_var,1,0), tf, clip = False),1,0)

        return self._output_data[k_data], self._output_data[k_mask], self._output_data[k_var]

if __name__ == '__main__':
    import argparse
    import hics.utils.datafile
    
    parser = argparse.ArgumentParser()    
    parser.add_argument('--input', help = 'input file (reflectance file)', required = True)
    parser.add_argument('--output', help = 'output file (hdr file)', required=True)
    parser.add_argument('--clean', help = 'leave only hdr data in output file', action='store_true')
    
    args = parser.parse_args()
    
    input_data, output_data =  hics.utils.datafile.migrate_base_data(args, 'hics.datafile.merge')
    
    if False:
        for k in list(output_data.keys()):
            if k.startswith('transform'):
                del output_data[k]
                
        output_data.vacuum()
    
    hdr = HDRMaker(input_data, output_data)
    im_ids = hdr._im_ids
    
    #Detect descriptors
    for im_id in im_ids:
        hdr.get_descriptors(im_id)
            
    #Match descriptors
    for im_i, im_j in itertools.product(im_ids, im_ids):
        hdr.get_match(im_i, im_j)
        
    for i in im_ids:
        hdr.get_transformed_image(i)
        
    from matplotlib import pyplot as plt
    
    minshape = min([hdr.get_transformed_image(im_id)[0].shape for im_id in im_ids if hdr.get_transformed_image(im_id)[0] is not None])
    
    if 'hdr_data' not in output_data:
        output_data['hdr-data'] = EmptyNDArray(minshape)
        output_data['hdr-data_max'] = EmptyNDArray(minshape)
        output_data['hdr-data_min'] = EmptyNDArray(minshape)
        output_data['hdr-var'] = EmptyNDArray(minshape)
        output_data['hdr-mask'] = EmptyNDArray(minshape)
        output_data['hdr-coeff'] = EmptyNDArray(minshape)
        
    hdr_data = output_data['hdr-data']
    hdr_var = output_data['hdr-var']
    hdr_mask = output_data['hdr-mask']
    hdr_data_min = output_data['hdr-data_min']
    hdr_data_max = output_data['hdr-data_max']
    hdr_coeff = output_data['hdr-coeff']
    
    hdr_data[:, :, :] = 0
    hdr_data_min[:, :, :] = 0
    hdr_data_max[:, :, :] = 0
    hdr_var[:, :, :] = 0
    hdr_mask[:, :, :] = 0
    hdr_coeff[:, :, :] = 0
    
    for im_id in im_ids:
        print(im_id)
        data, mask, var = hdr.get_transformed_image(im_id)
        if data is None:
            continue
        data = data[:minshape[0], :minshape[1], :minshape[2]]
        mask = mask[:minshape[0], :minshape[1], :minshape[2]]
        var = var[:minshape[0], :minshape[1], :minshape[2]]
        
        valid = (0 == mask)
        #sqrt(3*var) is half the span of a uniform
        data_min = (data - numpy.sqrt(3 * hdr_var))
        data_max = (data + numpy.sqrt(3 * hdr_var))
        data_min = numpy.minimum(hdr_data_min, data_min) * (hdr_mask != 0) + data_min * (hdr_mask == 0)
        data_max = numpy.maximum(hdr_data_max, data_max) * (hdr_mask != 0) + data_max * (hdr_mask == 0)
        
        hdr_data_min[:, :, :] = hdr_data_min * (1 - valid) + (data_min) * valid
        hdr_data_max[:, :, :] = hdr_data_max * (1 - valid) + (data_max) * valid
        hdr_mask += valid
        
        gl_factor = numpy.abs(scipy.ndimage.filters.gaussian_laplace(numpy.ma.MaskedArray(data, mask).mean(2), 1)[:, :, numpy.newaxis]) ** 2
        hdr_data += gl_factor * valid * data
        hdr_coeff += gl_factor * valid
    
    hdr_data[:, :, :] = hdr_data / hdr_coeff
    hdr_var[:, :, :] = (hdr_data_max - hdr_data_min) ** 2 / 12
    hdr_mask[:, :, :] = (hdr_mask == 0)
    
    output_data['hdr'] = numpy.ma.MaskedArray(hdr_data, hdr_mask)
    
    if args.clean:
        keys = list(output_data.keys())
        for k in keys:
            if k.startswith('descr-') or \
               k in ('center_id', 'hdr-coeff', 'hdr-data', 'hdr-mask', 'hdr-data_min', 'hdr-data_max', 'match_matrix') or \
               k.startswith('match-') or k.startswith('transform-') or k.startswith('transformed-'):
                del output_data[k]
    output_data.vacuum()
