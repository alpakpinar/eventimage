#!/usr/bin/env python

import os
import argparse
from datetime import datetime

from tqdm import tqdm

from lib.hasher import MD5Hasher
from lib.plotmaker import Plot2DMaker
from lib.rootfile import RootFile
from lib.genjetcleaner import GenJetCleaner

pjoin = os.path.join

class Job():
    '''Wrapper class to execute the plotting.'''
    def __init__(self, infile, tag, genJetCleaning=True, pfTypes=['all'], numEvents=5, jetsOnly=False) -> None:
        self.infile = infile
        self.tag = tag
        
        # Only take the RECO jets that match to a GEN jet with dR=0.4
        self.genJetCleaning = genJetCleaning
        
        self.pfTypes = pfTypes
        self.numEvents = numEvents
        # Event image for jet-based PF candidates, or all PF candidates?
        self.jetsOnly = jetsOnly

        # Important: We do NOT have filtered images for jets, 
        # so pfTypes=["all"] if we're looking at jets only
        if self.jetsOnly:
            self.pfTypes = ["all"]

        self.datasetName = self._extract_dataset_name()

    def _extract_dataset_name(self):
        '''Get the dataset name from the input file name.'''
        basename = ''.join(self.infile.split('/')[-1])
        temp = basename.replace('.root','').split('_')
        return '_'.join(temp[1:])

    def _make_plot_wrapper(self, masked_data, ievent, pfType):
        plotMaker = Plot2DMaker(masked_data, 
            tag=self.tag, 
            pfType=pfType, 
            jetsOnly=self.jetsOnly,
            datasetName=self.datasetName
            )
        
        plotMaker.make_plot(ievent)

    def run(self):
        # Record the MD5 hash of the input file
        MD5Hasher(self.infile).write_hash_to_file(self.tag)
        
        # Get the data (jet candidates + event images) with the VBF cuts applied
        masked_data = RootFile(self.infile).get_masked_candidates()

        # Only plot the jets that are matching to a GEN-level jet with dR=0.4
        if self.genJetCleaning:
            cleaner = GenJetCleaner(masked_data['jets'], masked_data['genJets'])
            masked_data['jets'] = cleaner.get_clean_jets()
            masked_data['non_matching_jets'] = cleaner.get_nonmatching_jets()

        # Loop over the events and make an image plot for each
        for ievent in tqdm(range(self.numEvents)):
            try:
                for pfType in self.pfTypes:
                    self._make_plot_wrapper(
                        masked_data, 
                        ievent=ievent, 
                        pfType=pfType, 
                        )
            
            except IndexError:
                print('At the end of file: Finishing job.')
                print(f'Processed {ievent} events.')
                break

def parse_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('inpath', help='Path to the input ROOT file.')
    parser.add_argument('--tag', help='The output tag.', default=f'{datetime.now().strftime("%Y-%m-%d")}_run')
    parser.add_argument('--numEvents', help='The number of events to run on.', type=int, default=5)
    parser.add_argument('--jetsOnly', action='store_true', help='Plot jet based images.')
    args = parser.parse_args()
    return args

def main():
    args = parse_cli()

    PFTYPES = [
        'all',
        # 'NeutralHadron',
        # 'ChargedHadron',
        # 'HFEM',
        # 'HFHadronic',
        # 'HighPuppiWeight',
    ]

    # Define the plotting job and run!
    job = Job(
        infile=args.inpath,
        tag=args.tag,
        pfTypes=PFTYPES,
        numEvents=args.numEvents,
        jetsOnly=args.jetsOnly
    )

    job.run()

if __name__ == '__main__':
    main()
