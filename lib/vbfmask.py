import numpy as np

class VBFMask():
    def __init__(self, jets) -> None:
        self.jets = jets
    
    def evaluate_mask(self):
        # Input data already has detajj + dphijj mask!
        diak4 = self.jets[:,:2].distincts()
        mask = (diak4.i0.pt > 80) & (diak4.i1.pt > 40)

        return mask.flatten()
