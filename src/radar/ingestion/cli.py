"""Run with python -m radar.ingestion (inside the same container/data volume)."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description='RADAR: ingestão rastreável e aprovação de dados reais')
    parser.add_argument('--data-dir',help='Diretório de dados separado (recomendado para testes)')
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('manifest');p.add_argument('--download',action='store_true')
    p=sub.add_parser('inspect');p.add_argument('batch')
    p=sub.add_parser('approve');p.add_argument('batch');p.add_argument('--reviewer',required=True);p.add_argument('--note',required=True);p.add_argument('--accept-alerts',action='store_true');p.add_argument('--fields',nargs='+')
    p=sub.add_parser('publish');p.add_argument('batch')
    sub.add_parser('list')
    p=sub.add_parser('ptax');p.add_argument('start');p.add_argument('end')
    p=sub.add_parser('yahoo');p.add_argument('symbol');p.add_argument('start');p.add_argument('end')
    p=sub.add_parser('sec');p.add_argument('company');p.add_argument('cik')
    args=parser.parse_args()
    from radar import data
    if args.data_dir:data.ROOT=Path(args.data_dir)
    from radar.ingestion import pipeline as pipe
    try:
        if args.command=='prepare':
            path=Path(args.manifest)
            result=pipe.stage(json.loads(path.read_text()),base_dir=path.parent,allow_download=args.download)
        elif args.command=='inspect':result=pipe.get_batch(args.batch)
        elif args.command=='approve':result=pipe.approve(args.batch,args.reviewer,args.note,accept_alerts=args.accept_alerts,fields=args.fields)
        elif args.command=='publish':result=pipe.publish(args.batch)
        elif args.command=='list':result=pipe.batches().astype(str).to_dict('records')
        elif args.command=='sec':result=pipe.save_snapshot(pipe.fetch_sec_companyfacts(args.company,args.cik))
        elif args.command=='ptax':result=pipe.save_snapshot(pipe.fetch_ptax(args.start,args.end))
        elif args.command=='yahoo':result=pipe.save_snapshot(pipe.fetch_yahoo(args.symbol,args.start,args.end))
        print(pipe.dumps(result))
    except (ValueError,OSError,KeyError) as error:
        parser.exit(1,str(error)+'\n')


if __name__=='__main__':main()
