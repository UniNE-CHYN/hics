import hics.utils.datafile

def fill_holes(image):
    """Fill holes of 2D hyperspectral image by using spatial linear interpolation"""
    if not hasattr(image, "mask"):
        image = numpy.ma.masked_invalid(image)
    image_out = image.copy()
    holes = []
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            if not numpy.all(image.mask[y, x]):
                for l in numpy.nonzero(image.mask[y, x])[0]:
                    holes.append((y, l))
    holes_tuples = list(sorted(set(holes)))
    #holes = numpy.array(numpy.nonzero(image.mask.sum(1))).T   
    #holes_tuples=[tuple(x) for x in list(holes)]
    
    for hole_y,hole_w in holes_tuples:
        up_valid,down_valid=hole_y,hole_y
        while up_valid>=0 and (up_valid,hole_w) in holes_tuples:
            up_valid-=1
        while down_valid<image.shape[0] and (down_valid,hole_w) in holes_tuples:
            down_valid+=1
        
        if up_valid==-1 and down_valid==image.shape[0]:
            #Whole columnn is empty 
            pass #Nothing fixable here
        elif up_valid==-1:
            #image_out[hole_y,:,hole_w] = image[down_valid,:,hole_w]
            pass
        elif down_valid==image.shape[0]:
            #image_out[hole_y,:,hole_w] = image[up_valid,:,hole_w]
            pass
        else:
            #Interpolate spatially
            image_out[hole_y,:,hole_w] = ((down_valid-hole_y)*image[up_valid,:,hole_w] + (hole_y-up_valid)*image[down_valid,:,hole_w])/(down_valid-up_valid)

    return image_out.filled(0)    

if __name__ == '__main__':
    import argparse
    from mmappickle import mmapdict
    import numpy
    
    parser = argparse.ArgumentParser()    
    parser.add_argument('--input', help = 'input file (reflectance file)', required = True)
    parser.add_argument('--output', help = 'output file (hdr file)', required=True)
    parser.add_argument('--filled', help = 'filled transform', action='store_true')
    parser.add_argument('--mnf', help = 'MNF transform', action='store_true')
    parser.add_argument('--pca', help = 'PCA transform', action='store_true')
    parser.add_argument('--key', help = 'Key to use', default='hdr')
    
    args = parser.parse_args()
    
    input_data, output_data =  hics.utils.datafile.migrate_base_data(args, 'hics.datafile.transform')
    
    #FIXME: variance?
    
    output_data[args.key] = input_data[args.key]
    
    if args.filled or args.mnf or args.pca:
        output_data[args.key+'-filled'] = fill_holes(output_data[args.key])
        
    if args.mnf:
        import spectral
        
        image = output_data[args.key+'-filled']
        #This is the reverse of the numpy masked array mask, 1 values will be used
        mask = numpy.ma.masked_invalid(output_data[args.key]).mask.sum(2) < image.shape[2] // 2
        
        deltas = image[:-1, :-1, :] - image[1:, 1:, :]
        deltas_mask = (mask[:-1, :-1].astype(numpy.int) + mask[1:, 1:].astype(numpy.int)) == 2
        
        
        signal = spectral.calc_stats(image, mask=mask)
        noise = spectral.calc_stats(deltas, mask=deltas_mask)
        noise.cov /= 2.0        
        #noise = spectral.noise_from_diffs( img[img.shape[0]//2-25:img.shape[0]//2+25, img.shape[1]//2-25:img.shape[1]//2+25,...])
        #import IPython
        #IPython.embed()
        mnfr = spectral.mnf(signal, noise)
        mnfimage = numpy.ma.MaskedArray(mnfr.reduce(image, num=image.shape[2]),numpy.repeat(~mask[:,:,numpy.newaxis],image.shape[2]))
        
        output_data[args.key+'-mnf-transform'] = mnfr                                           
        output_data[args.key+'-mnf'] = mnfimage
        
    if args.pca:
        raise NotImplemented("PCA should be implemented")
        
    if not args.filled:
        del output_data[args.key+'-filled']
        output_data.vacuum()
