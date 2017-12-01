if __name__ == '__main__':
    import sys, os
    from mmappickle import mmapdict
    import prettytable
    
    args = sys.argv[1:]
    
    if len(args) == 0:
        args = ['.']
        
    arg_exp = []
    for arg in args:
        if os.path.isdir(arg):
            for f in os.listdir(arg):
                arg_exp.append(os.path.join(arg, f))
        else:
            arg_exp.append(arg)
            
    t = prettytable.PrettyTable(['File', 'Type', 'Size', 'Description'])
    t.align["File"] = "l"
    t.align["Type"] = "l"
    t.align["Size"] = "r"
    t.align["Description"] = "l"
    t.sortby = 'File'
    t.set_style(prettytable.PLAIN_COLUMNS)
    t.header = False
    EMPTY_DESCR = '\n\n\n'
    for arg in arg_exp:
        if os.path.isdir(arg):
            t.add_row([arg, '<dir>', '', EMPTY_DESCR])
            continue
        
        try:
            hdr = open(arg, 'rb').read(2)
        except:
            t.add_row([arg, '<ERR>', None, 'Not readable'])
            continue
        
        size = os.path.getsize(arg)
        
        mmd = None
        if hdr == b'\x80\x04':
            try:
                mmd = mmapdict(arg, True)
            except:
                mmd = None
                
        if mmd is None:
            t.add_row([arg, '<file>', size, EMPTY_DESCR])
            continue
    
    
        if 'description' in mmd.keys():
            descr = mmd['description'].split('\n', 1)[0]
        else:
            descr = ''
        if descr == '':
            descr = '<no description>'
        
        from collections import Counter    
        keyc = list(Counter([k.split('-', 1)[0] for k in mmd.keys() if len(k.split('-')) in (1, 2) and not k.endswith('-var')]).items())
        keyc.sort(key=lambda x: (-x[1], x[0]))
        
        keyc_to_join = []
        for k in keyc:
            if k[1] == 1:
                keyc_to_join.append(k[0])
            else:
                keyc_to_join.append('{}×{}'.format(k[1], k[0]))
        
        if descr != '':
            descr += '\n'
            
        descr += ', '.join(keyc_to_join)
        t.add_row([arg, '<mmapdict>', size, descr + '\n'])
    
    print(t)
