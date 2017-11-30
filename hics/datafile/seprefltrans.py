import hics.utils.datafile

if __name__ == '__main__':
    import argparse
    from mmappickle import mmapdict
    import numpy
    
    parser = argparse.ArgumentParser()    
    parser.add_argument('--input', help = 'input file (hdr files)', required = True, nargs='+')
    parser.add_argument('--double', help = 'Light goes two times throug the sample', action='store_true')
    parser.add_argument('--pixelmargins', help = 'Number of pixels of the margins at the top and the bottom', type=int, default=5)
    parser.add_argument('--outputrefl', help = 'Reflectance output')
    parser.add_argument('--outputtrans', help = 'Transmittance output')
    
    args = parser.parse_args()
    
    data = [mmapdict(f, True) for f in args.input]
    hdrs = [numpy.ma.masked_invalid(d['hdr']) for d in data]
    
    from hscc.utils.multiregression import Multiregression
    mr = Multiregression(hdrs[0].shape, 2, multiprocess=False)    
    
    bgflist = []
    for hdr in hdrs:
        m1 = hdr[:args.pixelmargins, :, :].mean(0)
        m2 = hdr[-args.pixelmargins:, :, :].mean(0)
        
        bgf = numpy.ma.ones(hdr.shape+(2, ))
        bgf[:args.pixelmargins, :, :, 0] = hdr[:args.pixelmargins, :, :]
        bgf[-args.pixelmargins:, :, :, 0] = hdr[-args.pixelmargins:, :, :]
        for i in range(0, bgf.shape[0]):
            coeff = (i - args.pixelmargins / 2) / (bgf.shape[0]-args.pixelmargins)
            coeff = numpy.clip(coeff, 0, 1)
            bgf[i, :, :, 0] = (1 - coeff) * m1 + coeff * m2
        
        bgflist.append(bgf)
        mr.add_data(bgf[:, :, :, numpy.newaxis, :], hdr[..., numpy.newaxis, numpy.newaxis])
    
    T = numpy.ma.masked_invalid(mr.beta[:,:,:,0,0])
    R = numpy.ma.masked_invalid(mr.beta[:,:,:,1,0])
    
    T[T<0] = 0
    R[R<0] = 0
    
    if args.outputtrans is not None:
        dummy_input, output = hics.utils.datafile.migrate_base_data(args, 'hics.datafile.seprefltrans', override_input=args.input[0], override_output=args.outputtrans)
        output['hdr'] = T
        
    if args.outputrefl is not None:
        dummy_input, output = hics.utils.datafile.migrate_base_data(args, 'hics.datafile.seprefltrans', override_input=args.input[0], override_output=args.outputrefl)
        output['hdr'] = R
