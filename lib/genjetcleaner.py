#!/usr/bin/env python

import os
import numpy as np

class GenJetCleaner():
    def __init__(self,jets,genJets):
        self.jets = jets
        self.genJets = genJets

    def get_clean_jets(self, deltaRCut=0.4):
        matches_gen_jet = self.jets.match(self.genJets, deltaRCut=deltaRCut)
        return self.jets[matches_gen_jet]
    
    def get_nonmatching_jets(self, deltaRCut=0.4):
        matches_gen_jet = self.jets.match(self.genJets, deltaRCut=deltaRCut)
        return self.jets[~matches_gen_jet]