#!/usr/bin/env python

import os
import sys
import re
import uproot
import numpy as np
import mplhep as hep
import pandas as pd

from matplotlib import pyplot as plt
from tqdm import tqdm

pjoin = os.path.join


class DijetHelper():
    def __init__(self, df) -> None:
        self.df = df
    def get_dijet_variables(self, branchname) -> tuple:
        v0 = self.df[branchname].apply(lambda x: x[0])
        v1 = self.df[branchname].apply(lambda x: x[1])
        return v0, v1

class PlotSaver():
    def __init__(self, figure) -> None:
        self.outdir = './output'
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

        self.figure = figure

    def save(self, variable) -> None:
        outpath = pjoin(self.outdir, f'test_{variable}.pdf')
        self.figure.savefig(outpath)
        plt.close(self.figure)

class HistogramMaker():
    def __init__(self) -> None:
        self.binnings = {
            'detajj' : np.linspace(0,8,81),
            'dphijj' : np.linspace(0,np.pi),
            'ak4_pt0' : np.arange(0,1000,50),
        }
    def make_histogram(self, variable, array):
        h, xedges = np.histogram(array, bins=self.binnings[variable])
        return h, xedges

class PlotMaker():
    def __init__(self, histogram, xedges) -> None:
        self.histogram = histogram
        self.xedges = xedges

        self.ylims = {
            'detajj' : (1e-1,1e3),
            'dphijj' : (1e-1,1e3),
            'ak4_pt0' : (1e-1,1e5),
        }

    def make_plot(self, xlabel, variablename):
        fig, ax = plt.subplots()

        hep.histplot(
            self.histogram,
            self.xedges,
            ax=ax
        )
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Counts")
        ax.set_yscale('log')
        ax.set_ylim( self.ylims[variablename] )
        
        ax.text(0,1,'Test: VBF H(inv)',
            fontsize=14,
            ha='left',
            va='bottom',
            transform=ax.transAxes
        )

        PlotSaver(fig).save(variablename)


def compute_dphi(v0, v1) -> pd.Series:
    x = np.abs(v0 - v1)
    sign = x <= np.pi
    dphi = sign* x + ~sign * (2*np.pi - x)
    return dphi

def make_ak4_eta0_eta1_plot(df):
    '''Plot leading jet eta vs trailing jet eta'''
    ak4_eta0, ak4_eta1 = DijetHelper(df).get_dijet_variables('Jet_eta')

    fig, ax = plt.subplots()
    ax.scatter(ak4_eta0, ak4_eta1)
    ax.set_xlim(-5,5)
    ax.set_ylim(-5,5)

    ax.set_xlabel(r'Leading Jet $\eta$')
    ax.set_ylabel(r'Trailing Jet $\eta$')

    PlotSaver(fig).save('ak4_eta0_eta1')

def make_detajj_plot(df):
    ak4_eta0, ak4_eta1 = DijetHelper(df).get_dijet_variables('Jet_eta')

    detajj = np.abs(ak4_eta0 - ak4_eta1)

    h, xedges = HistogramMaker().make_histogram('detajj', detajj)
    
    PlotMaker(h, xedges).make_plot(
        xlabel=r'$\Delta\eta_{jj}$',
        variablename='detajj',
    )

def make_dphijj_plot(df):
    ak4_phi0, ak4_phi1 = DijetHelper(df).get_dijet_variables('Jet_phi')

    dphijj = compute_dphi(ak4_phi0, ak4_phi1)
    
    h, xedges = HistogramMaker().make_histogram('dphijj', dphijj)
    
    PlotMaker(h, xedges).make_plot(
        xlabel=r'$\Delta\phi_{jj}$',
        variablename='dphijj',
    )

def make_leading_jet_pt_plot(df):
    ak4_pt0, _ = DijetHelper(df).get_dijet_variables('Jet_pt')
    h, xedges = HistogramMaker().make_histogram('ak4_pt0', ak4_pt0)

    PlotMaker(h, xedges).make_plot(
        xlabel=r'Leading Jet $p_T$ (GeV)',
        variablename='ak4_pt0',
    )

def main():
    # Test plots + which function to use
    TEST_FUNCS = [
        make_ak4_eta0_eta1_plot,
        make_detajj_plot,
        make_dphijj_plot,
        make_leading_jet_pt_plot,
    ]

    infile = uproot.open( sys.argv[1] )
    df = infile['Events'].pandas.df(["nJet","Jet*"], flatten=False)

    # At least two jets!
    df = df[df["nJet"] > 1]

    for func in tqdm(TEST_FUNCS):
        func(df)

if __name__ == '__main__':
    main()