from mmappickle import mmapdict
import pickle
import numpy
import scipy.stats
import re
import os
from matplotlib import pyplot as plt
import hics.utils.datafile

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()    
    parser.add_argument('--input', help = 'input file', required = True)
    parser.add_argument('--calibration', help = 'calibration file', required=False)
    parser.add_argument('--min', type = int, default = 0, help = 'minimal valid luminosity')
    parser.add_argument('--max', type = int, default = 14000, help = 'maximal valid luminosity')
    parser.add_argument('--bad_deviation', type = float, default = 0.1, help = 'acceptable pixel deviation from average')
    parser.add_argument('--white_variance_threshold', type = float, default = 0.1, help = 'maximum accepted variance in white frames')
    parser.add_argument('--output', help = 'output file', required=True)
    parser.add_argument('--cropframes', help = 'crop n frames before and after each scan')
    
    args = parser.parse_args()
    input_data, output_data =  hics.utils.datafile.migrate_base_data(args, 'hics.datafile.'+os.path.splitext(os.path.basename(__file__))[0])
    if args.calibration is not None:
        calibration_data = pickle.load(args.calibration)
    else:
        calibration_data = None
        
    #white noise?
    white_frames = {}
    white_frames_min = {}
    white_frames_max = {}
    for k in sorted(input_data.keys()):
        if re.match('^white-[0-9]{5}$', k):  # or k == 'white':
            print("Processing {}...".format(k))
            white = numpy.array(input_data[k], dtype = numpy.float)
            
            if args.cropframes is not None:
                white = white[:, args.cropframes:-args.cropframes, :]
            if numpy.count_nonzero(white>args.max) / white.shape[1] > 200:
                #Too many bad pixels, we may have some saturation, so abort!
                print("... saturated :-(")
                continue
            white -= numpy.linspace(1, 0, white.shape[1])[numpy.newaxis, :, numpy.newaxis] * input_data[k+'-d0'].mean(1)[:, numpy.newaxis, :]
            white -= numpy.linspace(0, 1, white.shape[1])[numpy.newaxis, :, numpy.newaxis] * input_data[k+'-d1'].mean(1)[:, numpy.newaxis, :]
            
            white_normalized = white / white.mean(1)[:, numpy.newaxis, :]
            #Assume some kind of uniform distribution.
            white_normalized_variance = (white_normalized.max(1)-white_normalized.min(1)) ** 2 / 12
            white_normalized_variance[numpy.isnan(white_normalized_variance)] = numpy.inf
            white_normalized_variance[white_normalized_variance > args.white_variance_threshold] = numpy.inf
            
            white_data = numpy.ma.concatenate([white.min(1), white.max(1)], 0)
            
            
            average_intensities = numpy.ones(white_data.shape[0])
            for i in range(10):
                average_spectrum = (white_data * average_intensities[:, numpy.newaxis]).mean(0)
                average_intensities = (white_data / average_spectrum[numpy.newaxis, :]).mean(1)
                
            average_frame = average_intensities[:,numpy.newaxis]*average_spectrum[numpy.newaxis,:]
            
            delta = numpy.abs(average_frame - white_data) 
            delta = (delta[:white.shape[0], ...] + delta[white.shape[0]:, ...]) / (2 * numpy.average(white, 1))
            
            bad_pixels = numpy.logical_or(delta > args.bad_deviation, numpy.isinf(white_normalized_variance))
            white_normalized_variance[bad_pixels] = numpy.inf
            
            integration_time = input_data[k+'-p']['integration_time']
            
            white_frames[integration_time] = numpy.ma.MaskedArray(numpy.average(white, 1), bad_pixels) / integration_time
            
            white_frames_max[integration_time] = numpy.ma.MaskedArray(white.max(1), bad_pixels) / integration_time
            white_frames_min[integration_time] = numpy.ma.MaskedArray(white.min(1), bad_pixels) / integration_time
        
    white_frames_integration_times = numpy.array(list(sorted(white_frames.keys())))
        
    if args.calibration is None:
        for k in sorted(input_data.keys()):
            if re.match('^scan-[0-9]{5}$', k):  # or k == 'white':
                if k in output_data:
                    continue
                print("Computing reflectance for {!r}".format(k))
                data = numpy.ma.MaskedArray(input_data[k].copy(), dtype = numpy.float)
                data[data>args.max] = numpy.ma.masked
                integration_time = input_data[k+'-p']['integration_time']
                
                if k+'-d0-avg' in input_data.keys():
                    data -= numpy.linspace(1, 0, data.shape[1])[numpy.newaxis, :, numpy.newaxis] * input_data[k+'-d0-avg'][:, numpy.newaxis, :]
                    d0_std = numpy.sqrt(input_data[k+'-d0-var'])[:, numpy.newaxis, :] / integration_time
                elif k + '-d0' in input_data.keys():
                    data -= numpy.linspace(1, 0, data.shape[1])[numpy.newaxis, :, numpy.newaxis] * input_data[k+'-d0'].mean(1)[:, numpy.newaxis, :]
                    d0_std = numpy.sqrt(input_data[k+'-d0'].var(1))[:, numpy.newaxis, :] / integration_time
                    
                if k+'-d1-avg' in input_data.keys():
                    data -= numpy.linspace(0, 1, data.shape[1])[numpy.newaxis, :, numpy.newaxis] * input_data[k+'-d1-avg'][:, numpy.newaxis, :]
                    d1_std = numpy.sqrt(input_data[k+'-d1-var'])[:, numpy.newaxis, :] / integration_time
                elif k + '-d1' in input_data.keys():
                    data -= numpy.linspace(0, 1, data.shape[1])[numpy.newaxis, :, numpy.newaxis] * input_data[k+'-d1'].mean(1)[:, numpy.newaxis, :]
                    d1_std = numpy.sqrt(input_data[k+'-d1'].var(1))[:, numpy.newaxis, :] / integration_time
                    
                d_std = numpy.linspace(1, 0, data.shape[1])[numpy.newaxis, :, numpy.newaxis] * d0_std + \
                    numpy.linspace(0, 1, data.shape[1])[numpy.newaxis, :, numpy.newaxis] * d1_std
                    
                data /= integration_time
                data[data<args.min] = numpy.ma.masked
                
                output_data[k] = data
                output_data[k+'-p'] = input_data[k+'-p']
                
                if len(white_frames_integration_times) > 0:
                        
                    #find nearest integration time
                    best_white_frame_integration_time = white_frames_integration_times[numpy.argmin(numpy.abs(white_frames_integration_times - integration_time))]
                    white_frame = white_frames[best_white_frame_integration_time]
                    white_frame_min = white_frames_min[best_white_frame_integration_time]
                    white_frame_max = white_frames_max[best_white_frame_integration_time]
                    
                    #This MAY be a good idea, but the white frame estimation is probably enough
                    #refl_max = (data * (white_frame_max / white_frame)[:, numpy.newaxis, :] + 3 * d_std) / (white_frame_min[:, numpy.newaxis, :]) 
                    #refl_min = (data * (white_frame_min / white_frame)[:, numpy.newaxis, :] - 3 * d_std) / (white_frame_max[:, numpy.newaxis, :])                
                    refl_max = (data + 3 * d_std) / (white_frame_min[:, numpy.newaxis, :]) 
                    refl_min = (data - 3 * d_std) / (white_frame_max[:, numpy.newaxis, :])
    
                    refl = data / white_frame[:, numpy.newaxis, :]
                    
                    if k.startswith('scan-'):
                        newk = 'refl-' + k[5:]
                    else:
                        newk = 'refl-' + k
                    output_data[newk] = refl
                    #Assume uniform
                    output_data[newk+'-var'] = (refl_max - refl_min) ** 2 / 12
                    output_data[newk+'-p'] = input_data[k+'-p']
                    output_data[newk+'-w'] = white_frame
                
                #import IPython; from matplotlib import pyplot as plt; IPython.embed()                
            elif not k.startswith('scan-') and not k.startswith('white-') and not k in output_data:
                print(k)
                output_data[k] = input_data[k]
