#!/usr/bin/env python

import os
import sys
import re
import uproot
import numpy as np

from lib.genjetcleaner import GenJetCleaner

from coffea.analysis_objects import JaggedCandidateArray
from coffea.processor.dataframe import LazyDataFrame
from matplotlib import pyplot as plt
from tqdm import tqdm

pjoin = os.path.join

class PtChecker():
    def __init__(self, tree, tag, versiontag=None) -> None:
        '''
        Calculate the difference between transverse momentum of summed PF candidates within a jet
        and the NanoAOD value for the jet pt.
        '''
        self.tree = tree
        self.tag = tag
        self.versiontag = versiontag
        self._load_data()

    def _load_data(self):
        self.df = LazyDataFrame(self.tree, flatten=True)

    def setup_candidates(self):
        self.pfcands = JaggedCandidateArray.candidatesfromcounts(
            self.df['nPFCands'],
            pt=self.df['PFCands_pt'],
            eta=self.df['PFCands_eta'],
            phi=self.df['PFCands_phi'],
            mass=self.df['PFCands_pt'] * 0.,
            energy=self.df['PFCands_energy'],
            px=self.df['PFCands_px'],
            py=self.df['PFCands_py'],
        )

        # Filter out bad PF candidates, otherwise they cause errors down in the process
        self.pfcands = self.pfcands[self.pfcands.pt != 0.]

        self.jets = JaggedCandidateArray.candidatesfromcounts(
            self.df['nJet'],
            pt=self.df['Jet_pt'],
            rawpt=self.df['Jet_pt'] * (1 - self.df['Jet_rawFactor']),
            eta=self.df['Jet_eta'],
            phi=self.df['Jet_phi'],
            mass=self.df['Jet_phi'] * 0.,
        )

        genjets = JaggedCandidateArray.candidatesfromcounts(
            self.df['nGenJet'],
            pt=self.df['GenJet_pt'],
            eta=self.df['GenJet_eta'],
            phi=self.df['GenJet_phi'],
            mass=self.df['GenJet_phi'] * 0.,
        )

        # Only get the jets that are matched to GEN for this pt check!
        cleaner = GenJetCleaner(self.jets, genjets)
        self.jets = cleaner.get_clean_jets()

    def _get_matching_candidates(self, pfcands, jets):
        return pfcands.match(jets, deltaRCut=0.4)

    def compare_pts(self, ievent):
        # Get the indices of the matched jets
        matched_jetargs = self.pfcands.argmatch(self.jets, deltaRCut=0.4)[ievent]

        jet_pt = self.jets.rawpt[ievent]
        jet_eta = self.jets.eta[ievent]
        jet_phi = self.jets.phi[ievent]
        njet = len(jet_eta)
        
        fig, ax = plt.subplots()
        ax.scatter(jet_eta, jet_phi, marker='x', label='NanoAOD GEN-Matched Jets')
        
        ax.set_xlim(-5,5)
        ax.set_ylim(-3.5,3.5)

        ax.set_xlabel(r'Jet $\eta$')
        ax.set_ylabel(r'Jet $\phi$')

        for ijet in range(njet):
            # Get the set of PF candidates matching to ijet
            pfcands_px = self.pfcands.px[ievent][matched_jetargs == ijet]
            pfcands_py = self.pfcands.py[ievent][matched_jetargs == ijet]

            pfcands_eta = self.pfcands.eta[ievent][matched_jetargs == ijet]
            pfcands_phi = self.pfcands.phi[ievent][matched_jetargs == ijet]

            ax.scatter(pfcands_eta, pfcands_phi, marker='o', label=f'PF Candidates: Jet {ijet}')

            # Compute pt from these PF candidates
            pt_from_pf = np.hypot(np.sum(pfcands_px), np.sum(pfcands_py))
            diff = (jet_pt[ijet] - pt_from_pf) / jet_pt[ijet] * 100

            loc = jet_eta[ijet], jet_phi[ijet]
            ax.annotate(f'$p_T^{{Nano}} = {jet_pt[ijet]:.3f} \\ GeV$', 
                loc, 
                xytext=(loc[0], loc[1]+0.3) if jet_phi[ijet]<0 else (loc[0], loc[1]-0.5), 
                horizontalalignment='center'
                )
            
            ax.annotate(f'$p_T^{{PF}} = {pt_from_pf:.3f} \\ GeV$', 
                loc, 
                xytext=(loc[0], loc[1]+0.6) if jet_phi[ijet]<0 else (loc[0], loc[1]-0.8), 
                horizontalalignment='center'
                )

            ax.annotate(f'Diff: ${diff:.3f} \\% $', 
                loc, 
                xytext=(loc[0], loc[1]+0.9) if jet_phi[ijet]<0 else (loc[0], loc[1]-1.1), 
                horizontalalignment='center'
                )

        ax.legend()

        ax.text(0,1,f'ievent={ievent}',
                fontsize=12,
                ha='left',
                va='bottom',
                transform=ax.transAxes
            )

        if self.versiontag is not None:
            outdir = f'./output/{self.tag}/ptcheck/{self.versiontag}'
        else:
            outdir = f'./output/{self.tag}/ptcheck'
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        outpath = pjoin(outdir, f'ievent_{ievent}.pdf')
        fig.savefig(outpath)
        plt.close(fig)

def main():
    inpath = sys.argv[1]
    infile = uproot.open(inpath)
    tree = infile['Events']

    tag = ''.join(inpath.split('/')[-2])

    try:
        versiontag = re.findall('v\d', os.path.basename(inpath))[0]
    except IndexError:
        versiontag = None

    checker = PtChecker(tree, tag=tag, versiontag=versiontag)
    checker.setup_candidates()

    numEvents=10

    for ievent in tqdm(range(numEvents)):
        checker.compare_pts(ievent=ievent)

if __name__ == '__main__':
    main()