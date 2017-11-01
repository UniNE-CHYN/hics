def migrate_base_data(args, module):
    import os, subprocess
    from mmappickle import mmapdict
    
    input_data = mmapdict(args.input, True)
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
