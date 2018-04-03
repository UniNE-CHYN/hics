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
        return numpy.ma.masked_all(sp.shape), numpy.ma.masked_all(sp.shape)
    
    #plt.plot(wavelengths, sp)
    lastnzc = None
    for i in range(niter):
        spconv = numpy.polyval(numpy.polyfit(fit_wl, fit_sp, 4), wavelengths)
        
        nzc = numpy.count_nonzero(sp>spconv)
        if lastnzc is not None and lastnzc == nzc:
            break
        lastnzc = nzc
        
        fit_wl=numpy.concatenate([fit_wl, wavelengths[numpy.nonzero(sp>spconv)]])
        fit_sp=numpy.concatenate([fit_sp, sp[numpy.nonzero(sp>spconv)]])    
    
    return (sp / spconv), spconv

def remove_continuous_job(a):
    y, input_data, output_data, key = a
    
    
    hdrdata = output_data[key]
    hdrdata_conv = output_data[key+'-cont']
    wavelengths = output_data['wavelengths']
    
    
    for x in range(hdrdata.shape[1]):
        hdrdata[y, x], hdrdata_conv[y, x] = remove_continous(wavelengths, hdrdata[y, x])
    


if __name__ == '__main__':
    import argparse
    from mmappickle import mmapdict
    import numpy
    
    parser = argparse.ArgumentParser()    
    parser.add_argument('--input', help = 'input file (reflectance file)', required = True)
    parser.add_argument('--output', help = 'output file (hdr file)', required=True)
    parser.add_argument('--method', help = 'normalization method', choices=['percentile', 'removecont', 'whiten'], default='percentile')
    parser.add_argument('--percentile', help = 'normalization percentile', type=int, default=90)
    parser.add_argument('--wlfilter', help = 'filter wavelengths', type=str)
    parser.add_argument('--key', default='hdr', help = 'key to normalize', type=str)
    
    args = parser.parse_args()
    
    input_data, output_data =  hics.utils.datafile.migrate_base_data(args, 'hics.datafile.normalize')
    
    if args.wlfilter:
        wlfilter = hics.utils.datafile.get_range(args.wlfilter, len(input_data['wavelengths']))
        output_data['wavelengths'] = numpy.array(input_data['wavelengths'])[wlfilter]
    else:
        wlfilter = slice(None, None)
        
    
    if args.method == 'percentile':
        intensities = numpy.nanpercentile(numpy.ma.masked_invalid(input_data[args.key][:, :, wlfilter]).filled(numpy.nan),args.percentile,2)[:,:,numpy.newaxis]
        output_data[args.key] = input_data[args.key][:, :, wlfilter] / intensities
        if args.key+'-var' in input_data.keys():
            output_data[args.key+'-var'] = input_data[args.key+'-var'][:, :, wlfilter] / (intensities ** 2)
    elif args.method == 'whiten':
        data = numpy.ma.masked_invalid(input_data[args.key][:, :, wlfilter])
        
        output_data[args.key] = ((data - data.mean(2, keepdims=True)) / data.std(2, keepdims=True)).filled(numpy.nan)
    elif args.method == 'removecont':
        output_data[args.key] = input_data[args.key][:, :, wlfilter]
        output_data[args.key+'-cont'] = input_data[args.key][:, :, wlfilter]
        hdrdata = output_data[args.key]
        
        import multiprocessing, itertools
        pool = multiprocessing.Pool(processes=hics.utils.datafile.get_cpu_count())
        
        args = itertools.product(range(hdrdata.shape[0]), [input_data], [output_data], [args.key])
        
        pool.map(remove_continuous_job, args)
