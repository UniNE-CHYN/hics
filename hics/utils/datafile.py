def migrate_base_data(args, module, override_input=None, override_output=None):
    import os, subprocess
    from mmappickle import mmapdict
    
    if override_input is not None:
        input_data = mmapdict(override_input, True)
    else:
        input_data = mmapdict(args.input, True)
    
    if override_output is not None:
        output_data = mmapdict(override_output)
    else:
        output_data = mmapdict(args.output)
    output_data['description'] = input_data['description']
    output_data['wavelengths'] = input_data['wavelengths']
    if 'processing_steps' in input_data:
        processing_steps = input_data['processing_steps']
    else:
        processing_steps = []
    
    try:
        git_revision = subprocess.check_output(['git', 'describe', '--match=NeVeRmAtChRandoMJuNK', '--always', '--abbrev=40', '--dirty'], cwd=os.path.dirname(__file__)).strip()
    except:
        git_revision = None
    
    this_step_params = {}
    for k, v in args._get_kwargs():
        this_step_params[k] = v
    processing_steps.append((module, git_revision, this_step_params))
    output_data['processing_steps'] = processing_steps
    
    return input_data, output_data

def get_cpu_count(args=None):
    import multiprocessing, os
    if args is not None and args.parallel is not None:
        numcpus = args.parallel
    elif 'WINGDB_ACTIVE' in os.environ:
        numcpus = 1
    elif 'SLURM_JOB_CPUS_PER_NODE' in os.environ:
        numcpus = int(os.environ['SLURM_JOB_CPUS_PER_NODE'])
    else:
        numcpus = multiprocessing.cpu_count()
    
    return numcpus

def get_range(s, length=None):
    import numpy, re
    if s == '':
        return None
    
    r = []
    for p in s.split(','):
        m = re.match('^(-?[0-9]+)(?:\:(-?[0-9]+)(?:\:(-?[0-9]+))?)?$', p)
        if m is None:
            raise ValueError("Invalid slice: {}".format(p))
        gr = []
        for i, g in enumerate(m.groups()):
            if g is None:
                gr.append(g)
                continue
            g = int(g)
            if g >= 0 or i == 2:  #Positive or step size
                gr.append(g)
            elif length is not None:
                gr.append(g+length)
            else:
                raise ValueError("Invalid slice: {} (negative value and no length provided)".format(p))  
        
        if gr[1] is None:
            r.append(gr[0])
        else:
            r += list(numpy.r_[slice(*gr)])
    
    return numpy.array(r)
