import hics.utils.datafile

if __name__ == '__main__':
    import argparse
    from mmappickle import mmapdict
    import numpy
    
    parser = argparse.ArgumentParser()    
    parser.add_argument('--input', help = 'input file (reflectance file)', required = True)
    parser.add_argument('--output', help = 'output file (hdr file)', required=True)
    parser.add_argument('--method', help = 'normalization method', choices=['percentile', 'removecont'], default='percentile')
    parser.add_argument('--percentile', help = 'normalization percentile', type=int, default=90)
    
    args = parser.parse_args()
    
    input_data, output_data =  hics.utils.datafile.migrate_base_data(args, 'hics.datafile.normalize')
    
    if args.method == 'percentile':
        intensities = numpy.nanpercentile(numpy.ma.masked_invalid(input_data['hdr']).filled(numpy.nan),args.percentile,2)[:,:,numpy.newaxis]
        output_data['hdr'] = input_data['hdr'] / intensities
        if 'hdr-var' in input_data.keys():
            output_data['hdr-var'] = input_data['hdr-var'] / (intensities ** 2)
    elif args.method == 'removecont':
        def remove_continous(wavelengths, sp, niter=10):
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
        
        output_data['hdr'] = input_data['hdr']
        hdrdata = input_data['hdr']
        wavelengths = input_data['wavelengths']
        for y in range(hdrdata.shape[0]):
            print(y)
            for x in range(hdrdata.shape[1]):
                output_data['hdr'][y, x] = remove_continous(wavelengths, hdrdata[y, x])
