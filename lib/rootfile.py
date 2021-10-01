import os
import uproot
import pandas as pd

from coffea.processor.dataframe import LazyDataFrame
from coffea.analysis_objects import JaggedCandidateArray

from .vbfmask import VBFMask

class RootFile():
    def __init__(self, inpath, branches=[
        "nJet", 
        "*Jet*",
        "SoftActivityJet*", 
        "*GenJet*",
        "JetIm*", 
        "MET_*", 
        "EventIm*"]) -> None:
        
        self.infile = uproot.open(inpath)
        self.branches = branches

        df = LazyDataFrame(self.infile['Events'], flatten=True)
        self._setup_candidates(df)

    def _setup_candidates(self,df):
        self.genJets = JaggedCandidateArray.candidatesfromcounts(
            df['nGenJet'],
            pt=df['GenJet_pt'],
            eta=df['GenJet_eta'],
            phi=df['GenJet_phi'],
            mass=df['GenJet_mass'],
        )
    
        self.jets = JaggedCandidateArray.candidatesfromcounts(
            df['nJet'],
            pt=df['Jet_pt'],
            eta=df['Jet_eta'],
            phi=df['Jet_phi'],
            mass=df['Jet_mass'],
        )
        
        # 2D eta/phi event images, store dummy four momenta
        self.eventImages = JaggedCandidateArray.candidatesfromcounts(
            df['nEventImage'],
            pt=df['EventImage_pixelsAfterPUPPI']*0.,
            eta=df['EventImage_pixelsAfterPUPPI']*0.,
            phi=df['EventImage_pixelsAfterPUPPI']*0.,
            mass=df['EventImage_pixelsAfterPUPPI']*0.,
            pixels=df['EventImage_pixelsAfterPUPPI'],
            hfHardonicPixels=df['EventImage_HFHadronicPixels'],
            hfEMPixels=df['EventImage_HFEMPixels'],
            chargedHadronPixels=df['EventImage_ChargedHadronPixels'],
            neutralHadronPixels=df['EventImage_NeutralHadronPixels'],
        )

        self.eventImageSizeEta = df['EventImageSize_nEtaBins']
        self.eventImageSizePhi = df['EventImageSize_nPhiBins']

        self.jetImages = JaggedCandidateArray.candidatesfromcounts(
            df['nJetImage'],
            pt=df['JetImage_pixels']*0.,
            eta=df['JetImage_pixels']*0.,
            phi=df['JetImage_pixels']*0.,
            mass=df['JetImage_pixels']*0.,
            pixels=df['JetImage_pixels'],
        )

        self.jetImageSizeEta = df['JetImageSize_nEtaBins']
        self.jetImageSizePhi = df['JetImageSize_nPhiBins']

    @property
    def dataframe(self):
        return self.df

    @property
    def numevents(self):
        return self.df.size

    def get_masked_df(self):
        # Cuts are defined within VBFMask object
        mask = VBFMask(self.df).evaluate_mask()
        masked_df = self.df[mask].reset_index(drop=True)
        return masked_df

    def get_masked_candidates(self):
        '''
        Return a dictionary containing data for events which passed the VBF cuts.
        '''
        mask = VBFMask(self.jets).evaluate_mask()

        return {
            'jets' : self.jets[mask],
            'genJets' : self.genJets[mask],
            'eventImage_pixels' : self.eventImages.pixels[mask],
            'eventImage_nEta' : self.eventImageSizeEta[mask],
            'eventImage_nPhi' : self.eventImageSizePhi[mask],
            'jetImage_pixels' : self.jetImages.pixels[mask],
            'jetImage_nEta' : self.jetImageSizeEta[mask],
            'jetImage_nPhi' : self.jetImageSizePhi[mask],
        }