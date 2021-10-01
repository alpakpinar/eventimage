#!/usr/bin/env python

import os
import sys
import argparse
import numpy as np

from datetime import datetime
from lib.plotmaker import RatioPlotMaker
from lib.rootfile import RootFile

def parse_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('inpath1', help='Path to the first ROOT file.')
    parser.add_argument('inpath2', help='Path to the second ROOT file.')
    parser.add_argument('--tag', help='Tag for the job.', default=f'{datetime.now().strftime("%Y-%m-%d")}_ratio_run')
    parser.add_argument('--ievent', type=int, help='The event # to look at, default is the first event.', default=0)
    args = parser.parse_args()
    return args

def make_ratio_plot(args):
    masked_df1 = RootFile(args.inpath1).get_masked_df()
    masked_df2 = RootFile(args.inpath2).get_masked_df()

    PFTYPES = [
        'all',
        'NeutralHadron',
        'ChargedHadron',
        'HFEM',
        'HFHadronic',
        # 'HighPuppiWeight',
    ]

    for pfType in PFTYPES:
        ratioPlotMaker = RatioPlotMaker(
                [masked_df1, masked_df2],
                tag=args.tag,
                pfType=pfType,
                jetsOnly=False
                )
            
        ratioPlotMaker.make_ratio_plot(args.ievent)

def main():
    args = parse_cli()
    make_ratio_plot(args)

if __name__ == '__main__':
    main()