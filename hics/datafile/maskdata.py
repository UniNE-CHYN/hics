import scipy.ndimage
from mmappickle import mmapdict
import numpy
from matplotlib import pyplot as plt
import hics.utils.datafile

if __name__ == '__main__':
    import argparse, sys
    
    parser = argparse.ArgumentParser()    
    parser.add_argument('--input', help = 'input file', metavar='file.nhdr', required = True)
    parser.add_argument('--mask', help = 'mask file', metavar='mask.png', required=True)
    parser.add_argument('--output', help = 'output file', metavar='file.nmhdr', required=False)
    parser.add_argument('--wlid', help = 'wavelength id', type=int, required=False)
    
    args = parser.parse_args()
    
    
    
    if args.output is None:
        input_data = mmapdict(args.input, True)
        if args.wlid is None:
            dispdata = numpy.ma.average(numpy.ma.masked_invalid(input_data['hdr']), 2)
        else:
            print(args.wlid)
            dispdata = numpy.ma.masked_invalid(input_data['hdr'][:, :, args.wlid])
        ldispdata = numpy.log(dispdata)
        try:
            plt.imshow(ldispdata, cmap='gray', clim=(numpy.percentile(ldispdata, 1), numpy.percentile(ldispdata, 99))).write_png(args.mask, True)
        except TypeError:
            plt.imshow(ldispdata, cmap='gray', clim=(numpy.percentile(ldispdata, 1), numpy.percentile(ldispdata, 99))).write_png(args.mask)
            
        sys.exit(0)
    
    input_data, output_data =  hics.utils.datafile.migrate_base_data(args, 'hics.datafile.maskdata')
    
    mask = scipy.ndimage.imread(args.mask)[:, :, 0] == 0
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
