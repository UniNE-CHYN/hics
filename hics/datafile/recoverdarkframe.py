import hics.utils.datafile

if __name__ == '__main__':
    import argparse
    from mmappickle import mmapdict
    import numpy, scipy.optimize
    
    parser = argparse.ArgumentParser()    
    parser.add_argument('--input', help = 'input file (reflectance file)', required = True)
    parser.add_argument('--output', help = 'output file (hdr file)', required=True)
    parser.add_argument('--darkframedata', help = 'dark frame data', required=True)
    
    args = parser.parse_args()
    
    input_data, output_data =  hics.utils.datafile.migrate_base_data(args, 'hics.datafile.recoverdarkframe')
    darkframedata = mmapdict(args.darkframedata, False)
    
    dfms = {}
    for k in list(darkframedata.keys())[:]:
        if not (k.startswith('scan-') and len(k) == 10):
            continue
        
        if not k + '-dfm' in darkframedata.keys():
            d = darkframedata[k]
            A=numpy.ones((d.shape[1],2))
            A[:,0]=d.mean(2).mean(0)
            
            px={}
            for y in range(320):
                print(y)
                for wl in range(256):
                    px[y,wl]=numpy.linalg.lstsq(A,d[y,:,wl])
                    
            b0 = numpy.ma.empty((320,256))
            b1 = numpy.ma.empty((320,256))
            res = numpy.ma.empty((320,256))
            for y in range(320):
                for wl in range(256):
                    b0[y,wl] = px[y,wl][0][0]
                    b1[y,wl] = px[y,wl][0][1]
                    res[y,wl] = px[y,wl][1]
                    
            resmedian = numpy.median(res.compressed())
            resstd = numpy.std(res.compressed())
                    
            b0mean = b0.mean()
            b0std = b0.std()
            b0[b0 > b0mean + 3*b0std] = numpy.ma.masked
            b0[b0 < b0mean - 3*b0std] = numpy.ma.masked
            b0[res > resmedian + 3*resstd] = numpy.ma.masked
            b0[res < resmedian - 3*resstd] = numpy.ma.masked
            
            b1mean = b1.mean()
            b1std = b1.std()
            b1[b1 > b1mean + 3*b1std] = numpy.ma.masked
            b1[b1 < b1mean - 3*b1std] = numpy.ma.masked
            
            darkframedata[k + '-dfm'] = numpy.ma.concatenate([b0[:,numpy.newaxis,:], b1[:,numpy.newaxis,:]],1)
        
        dfms[darkframedata[k+'-p']['integration_time']] = darkframedata[k + '-dfm']
    
    for k in input_data.keys():
        if (k.startswith('scan-') and len(k) == 10) or (k.startswith('white-') and len(k) == 11):
            output_data[k] = input_data[k]
            if k + '-p' in input_data.keys():
                output_data[k+'-p'] = input_data[k+'-p']
            
            it = input_data[k+'-p']['integration_time']
            if it not in dfms:
                print("Integration time {} is not in dfms")
                continue
            
            dfm = dfms[it]
            d = input_data[k]
            dm = d - dfm[:,1, numpy.newaxis,:]
            
            def minfunc(v):
                fixed = dm - v*dfm[:,0,numpy.newaxis,:]
                r=numpy.percentile((numpy.var(fixed,0).mean(0)/numpy.var(fixed,1).mean(0)).compressed(), 90)
                if ((fixed < 0).sum(2) > 10).sum() > 0:
                    return numpy.inf
                return r
            
            r = scipy.optimize.minimize_scalar(minfunc)
                 
            dark_frame = dfm[:,1,numpy.newaxis,:] + r.x*dfm[:,0,numpy.newaxis,:]
                
            output_data[k+'-d0'] = dark_frame
            output_data[k+'-d1'] = dark_frame
            
