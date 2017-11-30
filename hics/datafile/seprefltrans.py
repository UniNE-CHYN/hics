import hics.utils.datafile

if __name__ == '__main__':
    import argparse
    from mmappickle import mmapdict
    import numpy
    from matplotlib import pyplot as plt
    
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
    mr_R = Multiregression(hdrs[0].shape, 1, multiprocess=False)
    mr_T = Multiregression(hdrs[0].shape, 1, multiprocess=False)
    
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
        mr.add_data(bgf[:, :, :, numpy.newaxis, :].filled(numpy.nan), hdr[..., numpy.newaxis, numpy.newaxis])
        mr_R.add_data(bgf[:, :, :, numpy.newaxis, 1:2].filled(numpy.nan), hdr[..., numpy.newaxis, numpy.newaxis])
        mr_T.add_data(bgf[:, :, :, numpy.newaxis, 0:1].filled(numpy.nan), hdr[..., numpy.newaxis, numpy.newaxis])
                    
                
    T = numpy.ma.masked_invalid(mr.beta[:,:,:,0,0])
    R = numpy.ma.masked_invalid(mr.beta[:,:,:,1,0])
    
    del mr
    
    Tidx = T < 0
    Ridx = R < 0
    
    R[Tidx] = mr_R.beta[..., 0, 0][Tidx]
    T[Ridx] = mr_T.beta[..., 0, 0][Ridx]
    
    T[Tidx] = 0
    R[Ridx] = 0    
    
    if args.outputtrans is not None:
        dummy_input, output = hics.utils.datafile.migrate_base_data(args, 'hics.datafile.seprefltrans', override_input=args.input[0], override_output=args.outputtrans)
        output['hdr'] = T
        
    if args.outputrefl is not None:
        dummy_input, output = hics.utils.datafile.migrate_base_data(args, 'hics.datafile.seprefltrans', override_input=args.input[0], override_output=args.outputrefl)
        output['hdr'] = R
