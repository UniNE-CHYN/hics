import hics.utils.datafile

def remove_continous(wavelengths, sp, niter=100):
    wavelengths = numpy.array(wavelengths)
    fit_wl = wavelengths.copy()
    fit_sp = sp.copy()
    
    if hasattr(fit_sp, "mask"):
        m = fit_sp.mask
    else:
        m = numpy.isnan(fit_sp)
        #no mask
        #m = numpy.zeros_like(fit_sp, dtype=numpy.bool)
    
    fit_wl = fit_wl[~m]
    fit_sp = fit_sp[~m]
    
    if len(fit_sp) < 5:
        return numpy.ma.masked_all(sp.shape)
    
    #plt.plot(wavelengths, sp)
    for i in range(niter):
        spconv = numpy.polyval(numpy.polyfit(fit_wl, fit_sp, 4), wavelengths)
        
        fit_wl=numpy.concatenate([fit_wl, wavelengths[numpy.nonzero(sp>spconv)]])
        fit_sp=numpy.concatenate([fit_sp, sp[numpy.nonzero(sp>spconv)]])    
    
    return sp / spconv

def remove_continuous_job(a):
    y, input_data, output_data = a
    
    
    hdrdata = output_data['hdr']
    wavelengths = output_data['wavelengths']
    
    for x in range(hdrdata.shape[1]):
        hdrdata[y, x] = remove_continous(wavelengths, hdrdata[y, x])
    


if __name__ == '__main__':
    import argparse
    from mmappickle import mmapdict
    import numpy
    
    parser = argparse.ArgumentParser()    
    parser.add_argument('--input', help = 'input file (reflectance file)', required = True)
    parser.add_argument('--output', help = 'output file (hdr file)', required=True)
    parser.add_argument('--method', help = 'normalization method', choices=['percentile', 'removecont'], default='percentile')
    parser.add_argument('--percentile', help = 'normalization percentile', type=int, default=90)
    parser.add_argument('--cropwl', help = 'crop wavelengths', type=int, default=0)
    
    args = parser.parse_args()
    
    input_data, output_data =  hics.utils.datafile.migrate_base_data(args, 'hics.datafile.normalize')
    
    if args.cropwl != 0:
        output_data['wavelengths'] = input_data['wavelengths'][args.cropwl:-args.cropwl]
    
    if args.method == 'percentile':
        intensities = numpy.nanpercentile(numpy.ma.masked_invalid(input_data['hdr'][:, :, args.cropwl:-args.cropwl]).filled(numpy.nan),args.percentile,2)[:,:,numpy.newaxis]
        output_data['hdr'] = input_data['hdr'][:, :, args.cropwl:-args.cropwl] / intensities
        if 'hdr-var' in input_data.keys():
            output_data['hdr-var'] = input_data['hdr-var'][:, :, args.cropwl:-args.cropwl] / (intensities ** 2)
    elif args.method == 'removecont':
        output_data['hdr'] = input_data['hdr'][:, :, args.cropwl:-args.cropwl]
        hdrdata = output_data['hdr']
        
        import multiprocessing, itertools
        pool = multiprocessing.Pool(processes=hics.utils.datafile.get_cpu_count())
        
        args = itertools.product(range(hdrdata.shape[0]), [input_data], [output_data])
        
        pool.map(remove_continuous_job, args)
