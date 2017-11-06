import hics.utils.datafile

if __name__ == '__main__':
    import argparse
    from mmappickle import mmapdict
    import numpy
    
    parser = argparse.ArgumentParser()    
    parser.add_argument('--input', help = 'input file (reflectance file)', required = True)
    parser.add_argument('--output', help = 'output file (hdr file)', required=True)
    parser.add_argument('--percentile', help = 'normalization percentile', type=int, default=90)
    
    args = parser.parse_args()
    
    input_data, output_data =  hics.utils.datafile.migrate_base_data(args, 'hics.datafile.normalize')
    
    intensities = numpy.nanpercentile(numpy.ma.masked_invalid(input_data['hdr']).filled(numpy.nan),args.percentile,2)[:,:,numpy.newaxis]
    output_data['hdr'] = input_data['hdr'] / intensities
    if 'hdr-var' in input_data.keys():
        output_data['hdr-var'] = input_data['hdr-var'] / (intensities ** 2)
