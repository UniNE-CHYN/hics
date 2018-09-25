if __name__ == '__main__':
    import argparse, os
    from mmappickle import mmapdict
    from pprint import pprint
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help = 'input folder', required = True)

    args = parser.parse_args()

    if not os.path.exists(os.path.join(args.input, 'description.txt')):
        samples = [os.path.join(args.input, d) for d in os.listdir(args.input) if os.path.exists(os.path.join(args.input, d, 'description.txt'))]
    else:
        samples = [args.input]

    sample_props = {}
    datapoints = {}
    for s in samples:
        sample_props[s] = dict([[x.strip() for x in l.split(':', 1)] for l in open(os.path.join(s, 'description.txt')).read().strip().split('\n')])
        if sample_props[s].get('type') == 'technical':
            continue
        for f in os.listdir(s):
            if not f.endswith('.mhdr'):
                continue

            data = mmapdict(os.path.join(s, f), True)
            mn = sample_props[s].get('name')
            if mn not in datapoints:
                datapoints[mn] = {}
            sample_name = ([x for x in os.path.split(s) if x != ''][-1], os.path.splitext(f)[0])
            hdr = data['hdr']
            if not hasattr(hdr, 'mask'):
                hdr = numpy.ma.masked_invalid(hdr)
            n_datapoints = ((~hdr.mask).sum(2) != 0).sum()
            datapoints[mn][sample_name] = n_datapoints


    #pprint(sample_props)
    minerals = [sp['name'] for sp in sample_props.values() if sp.get('type') == 'mineral']

    print("Number of samples: {}".format(len(minerals)))
    print("Number of distinct minerals: {}".format(len(set(minerals))))
    print("Number of datapoints: {}".format(sum([sum(datapoint.values()) for datapoint in datapoints.values()])))
    print("")

    print("Mineral name & Sample IDs & Datapoints \\\\ \\hline")
    for k in sorted(datapoints.keys()):
        dpl = []
        sample_ids = [x[0] for x in sorted(datapoints[k].keys())]

        for sample_id in sorted(set(sample_ids)):
            sic = sample_ids.count(sample_id)
            if sic == 1:
                dpl.append(sample_id)
            else:
                dpl.append('{}({})'.format(sample_id, sic))


        print('{} & {} & {} \\\\'.format(k, ', '.join(dpl), sum(datapoints[k].values())))

    print('\\hline')
    import IPython
    IPython.embed()
