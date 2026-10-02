import argparse
import json
from pathlib import Path
from .core import parse_data, validate, compare

def main():
    parser=argparse.ArgumentParser(description='Validate a dataset or compare contracts. Exit 1 for validation failure/breaking change, 2 for invalid input.')
    sub=parser.add_subparsers(dest='command',required=True)
    check=sub.add_parser('validate');check.add_argument('contract');check.add_argument('data');check.add_argument('--format',choices=['json','csv'],default='json')
    diff=sub.add_parser('compare');diff.add_argument('old');diff.add_argument('new')
    args=parser.parse_args()
    try:
        if args.command=='validate':
            report=validate(json.loads(Path(args.contract).read_text()),parse_data(Path(args.data).read_text(),args.format),args.format=='csv');failed=not report['valid']
        else:
            report=compare(json.loads(Path(args.old).read_text()),json.loads(Path(args.new).read_text()));failed=report['breaking']
        print(json.dumps(report,indent=2));return int(failed)
    except (ValueError,OSError) as error:
        print(json.dumps({'error':str(error)}));return 2
if __name__=='__main__': raise SystemExit(main())
