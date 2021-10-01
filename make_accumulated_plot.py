#!/usr/bin/env python

import os
import sys
import argparse
import numpy as np

from datetime import datetime
from lib.plotmaker import AccumulationPlotMaker
from lib.rootfile import RootFile

pjoin = os.path.join

def get_dataset_name(filename):
    temp = filename.replace('.root','').split('_')
    return '_'.join(temp[1:])

def parse_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('inpath', help='Path to the first ROOT file.')
    parser.add_argument('--tag', help='Tag for the job.', default=f'{datetime.now().strftime("%Y-%m-%d")}_accumulated_run')
    parser.add_argument('--numevents', type=int, help='Number of events to accumulate.', default=40)
    args = parser.parse_args()
    return args

def main():
    args = parse_cli()
    masked_df = RootFile(args.inpath).get_masked_df()

    plotter = AccumulationPlotMaker(masked_df, tag=args.tag, dataset=get_dataset_name(args.inpath))
    plotter.make_acc_plot(numevents=args.numevents)

if __name__ == '__main__':
    main()