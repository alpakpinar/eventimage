#!/usr/bin/env python

import os
import sys
import re
import uproot
import numpy as np
import mplhep as hep

from matplotlib import pyplot as plt

pjoin = os.path.join

def plot(tree, dataset_name):
    data = tree['nPFCands'].array()
    xedges = np.arange(0,200,5)

    h, _ = np.histogram(data, bins=xedges)

    fig, ax = plt.subplots()
    hep.histplot(h, xedges, ax=ax)

    ax.set_ylabel('Counts')
    ax.set_xlabel('Number of PF Candidates')

    outdir = f'./output'
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    outpath = pjoin(outdir, f'{dataset_name}_num_pf_cands.pdf')
    fig.savefig(outpath)
    plt.close(fig)

def main():
    # Path to input ROOT file
    inpath = sys.argv[1]

    infile = uproot.open(inpath)
    tree = infile['Events']

    dataset_name = os.path.basename(inpath).replace('nano_','').replace('.root','')

    plot(tree, dataset_name)

if __name__ == '__main__':
    main()