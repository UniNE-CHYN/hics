import os, shutil, h5py, numpy, re
from mmappickle import mmapdict

def convert_sample(input_dir, output_dir):
    sample_id = [x for x in os.path.split(input_dir) if x != ''][-1]
    if not os.path.exists(os.path.join(input_dir, 'description.txt')):
        raise ValueError("Invalid sample folder")

    #FIXME: validate and copy description.txt
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    print(input_dir)
    data = [[x for x in l.split(':', 1)] for l in open(os.path.join(input_dir, 'description.txt')).read().strip().split('\n')]
    out_desc = open(os.path.join(output_dir, sample_id+'-'+'description.txt'), 'w')
    for k, v in data:
        out_desc.write('{}: {}\r\n'.format(k.lower(), v))
    out_desc.close()


    for scan_id in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if not os.path.exists(os.path.join(input_dir, scan_id+'.mhdr')):
            continue

        for f in [scan_id+'.scan', scan_id+'.hdr', scan_id+'.mhdr', sample_id+'-'+scan_id+'.ply', sample_id+'-'+scan_id+'.png'] + \
            ['{}-im-{:03d}.jpg'.format(scan_id, i) for i in range(0, 361, 10)]:
            if not os.path.exists(os.path.join(input_dir, f)):
                print("Missing file: ", os.path.join(input_dir, f))
                continue
            if not f.endswith('.scan') and not f.endswith('.hdr') and not f.endswith('.mhdr'):
                if f.startswith('{}-'.format(scan_id)):
                    shutil.copyfile(os.path.join(input_dir, f), os.path.join(output_dir, sample_id+'-'+f))
                else:
                    shutil.copyfile(os.path.join(input_dir, f), os.path.join(output_dir, f))
            else:
                infile = mmapdict(os.path.join(input_dir, f), True)
                outfile = h5py.File(os.path.join(output_dir, sample_id+'-'+f+'.h5'), 'w')

                wavelengths = numpy.array(infile['wavelengths'])
                outfile.create_dataset("wavelengths", wavelengths.shape, dtype=wavelengths.dtype)
                outfile['wavelengths'][:] = wavelengths

                k_list = sorted([k for k in infile.keys() if k.startswith('scan-') and k.endswith('-p')])
                integration_times = numpy.array([infile[k]['integration_time'] for k in k_list])

                if len(integration_times) > 0:

                    outfile.create_dataset("integration_times", integration_times.shape, dtype=numpy.float32)
                    outfile['integration_times'][:] = integration_times


                for k in infile.keys():
                    if not re.match('^(scan|white)-([0-9]+)(-d0|-d1)?$', k) and not k in ('hdr', ):
                        continue
                    if hasattr(infile[k], 'mask'):
                        data = infile[k].filled(numpy.nan)
                    else:
                        data = infile[k]

                    data = numpy.transpose(data, (2, 0, 1))

                    if f.endswith('.scan'):
                        outfile.create_dataset(k, data.shape, dtype=numpy.uint16)
                    else:
                        outfile.create_dataset(k, data.shape, dtype=numpy.float32)
                    outfile[k][...] = data[...]

def write_envi_template(fn):
    f = open(fn, 'w')
    f.write('<?xml version="1.0" encoding="utf-8"?>\n')
    f.write("""<ENVI_FILE_TEMPLATE>""")
    f.write("""<HDF5 name="fasnacht-hicsdata (HDR)"><RASTER interleave="bsq"><DATASET>//hdr</DATASET><METADATA name="WAVELENGTH" id="//wavelengths"/><METADATA name="WAVELENGTH UNITS">Nanometers</METADATA></RASTER></HDF5>""")
    f.write("""<HDF5 name="fasnacht-hicsdata (SCAN)">""")
    for i in range(10):
        f.write("""<RASTER interleave="bsq"><DATASET>//scan-{:05d}</DATASET><METADATA name="WAVELENGTH" id="//wavelengths"/><METADATA name="WAVELENGTH UNITS">Nanometers</METADATA></RASTER>""".format(i))
        f.write("""<RASTER interleave="bsq"><DATASET>//scan-{:05d}-d0</DATASET><METADATA name="WAVELENGTH" id="//wavelengths"/><METADATA name="WAVELENGTH UNITS">Nanometers</METADATA></RASTER>""".format(i))
        f.write("""<RASTER interleave="bsq"><DATASET>//scan-{:05d}-d1</DATASET><METADATA name="WAVELENGTH" id="//wavelengths"/><METADATA name="WAVELENGTH UNITS">Nanometers</METADATA></RASTER>""".format(i))
        f.write("""<RASTER interleave="bsq"><DATASET>//white-{:05d}</DATASET><METADATA name="WAVELENGTH" id="//wavelengths"/><METADATA name="WAVELENGTH UNITS">Nanometers</METADATA></RASTER>""".format(i))
        f.write("""<RASTER interleave="bsq"><DATASET>//white-{:05d}-d0</DATASET><METADATA name="WAVELENGTH" id="//wavelengths"/><METADATA name="WAVELENGTH UNITS">Nanometers</METADATA></RASTER>""".format(i))
        f.write("""<RASTER interleave="bsq"><DATASET>//white-{:05d}-d1</DATASET><METADATA name="WAVELENGTH" id="//wavelengths"/><METADATA name="WAVELENGTH UNITS">Nanometers</METADATA></RASTER>""".format(i))
    f.write("""</HDF5>""")


    f.write("""</ENVI_FILE_TEMPLATE>""")
    f.close()

if __name__ == '__main__':
    import argparse, os
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help = 'input folder', required = True)
    parser.add_argument('--output', help = 'output folder', required=True)

    args = parser.parse_args()

    if not os.path.exists(os.path.join(args.input, 'description.txt')):
        samples = [(os.path.join(args.input, d), args.output) for d in os.listdir(args.input) if os.path.exists(os.path.join(args.input, d, 'description.txt'))]
    else:
        samples = [(args.input, args.output)]

    if not os.path.exists(args.output):
        os.mkdir(args.output)

    write_envi_template(os.path.join(args.output, 'envi_template.xml'))

    for input_dir, output_dir in samples:
        convert_sample(input_dir, output_dir)
