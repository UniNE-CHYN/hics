if __name__ == '__main__':
    import argparse
    from mmappickle import mmapdict
    
    parser = argparse.ArgumentParser()    
    parser.add_argument('--description', help = 'new description (first line)')
    parser.add_argument('--description_full', help = 'new description (all lines)')
    parser.add_argument('--vacuum', action="store_true", help='vaccum the file(s) after modification')
    parser.add_argument('files', nargs='+', help = 'files to modify')
    
    args = parser.parse_args()
    
    for f in args.files:
        d = mmapdict(f)
        if args.description_full is not None:
            d['description'] = args.description_full
        elif args.description is not None:
            if 'description' in d.keys():
                if '\n' in d['description']:
                    d['description'] = args.description + '\n' + d['description'].split('\n', 1)[1]
                else:
                    d['description'] = args.description
            else:
                d['description'] = args.description
                
        if args.vacuum:
            d.vacuum()

