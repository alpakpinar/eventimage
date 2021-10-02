import os
import re
import numpy as np

from .genjetcleaner import GenJetCleaner

from matplotlib import pyplot as plt
from matplotlib import colors

pjoin = os.path.join

class ColormeshPlotter():
    def __init__(self) -> None:
        '''Base class with ax.pcolormesh() call.'''
        pass

    def make_cmesh_plot(self, etaSize, phiSize, pixels, title=''):
        '''Base function for making a 2D colormesh plot.'''
        fig, ax = plt.subplots()
        
        etaBins = np.linspace(-5,5,etaSize)
        phiBins = np.linspace(-np.pi,np.pi,phiSize)

        cmap = ax.pcolormesh(etaBins, phiBins, pixels.T, norm=colors.LogNorm(vmin=1e-1, vmax=1e3))
        ax.set_xlabel(r'PF Candidate $\eta$')
        ax.set_ylabel(r'PF Candidate $\phi$')

        ax.set_title(title)

        cb = fig.colorbar(cmap,ax=ax)
        cb.set_label('PF Energy (GeV)')

        return fig, ax

class PlotSaver():
    def __init__(self, figure, outtag, jetsOnly=False) -> None:
        if jetsOnly:
            self.outdir = f'./output/{outtag}/jet_based_images'
        else:
            self.outdir = f'./output/{outtag}/event_images'
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

        self.figure = figure

    def save(self, outfilename) -> None:
        outpath = pjoin(self.outdir, outfilename)
        self.figure.savefig(outpath)
        plt.close(self.figure)

class Plot2DMaker(ColormeshPlotter):
    def __init__(self, data, tag, datasetName, pfType='all', jetsOnly=False) -> None:
        super().__init__()
        self.data = data
        self.tag = tag
        self.datasetName = datasetName
        # Type of PF candidate collection for the event image
        self.pfType = pfType
        # Only read the collection of PF candidates coming from jets?
        self.jetsOnly = jetsOnly
        self.tablename = "JetImage" if self.jetsOnly else "EventImage"

        self.dataset_tags = {
            'Z(\d)JetsToNuNu.*Pt.*FXFX.*' : r'QCD $Z(\nu\nu)$',
            'EWKZ2Jets.*ZToNuNu.*' : r'EWK $Z(\nu\nu)$',
            'VBF_HToInv.*M125.*' : r'VBF $H(inv)$',
        }

    def _get_dataset_tag(self, datasetName):
        for regex, tag in self.dataset_tags.items():
            if re.match(regex, datasetName):
                return tag

    def _get_data_for_event(self, ievent):
        dataForEvent = {}
        dataForEvent['jetPt'] = self.data['jets'].pt[ievent]
        dataForEvent['jetEta'] = self.data['jets'].eta[ievent]
        dataForEvent['jetPhi'] = self.data['jets'].phi[ievent]
        
        dataForEvent['nonMatchingJetPt'] = self.data['non_matching_jets'].pt[ievent]
        dataForEvent['nonMatchingJetEta'] = self.data['non_matching_jets'].eta[ievent]
        dataForEvent['nonMatchingJetPhi'] = self.data['non_matching_jets'].phi[ievent]

        self.tablename = 'eventImage' if not self.jetsOnly else 'jetImage'

        dataForEvent[f'{self.tablename}_pixels'] = self.data[f'{self.tablename}_pixels'][ievent]
        dataForEvent[f'{self.tablename}_nEta'] = self.data[f'{self.tablename}_nEta'][ievent]
        dataForEvent[f'{self.tablename}_nPhi'] = self.data[f'{self.tablename}_nPhi'][ievent]
        
        return dataForEvent

    def make_plot(self, ievent):
        '''Plot the 2D eta/phi map for event # ievent.'''
        # Get the data for this particular event
        dataForEvent = self._get_data_for_event(ievent)

        # Reshape the pixels into 2D format
        pixels_2d = np.reshape(dataForEvent[f'{self.tablename}_pixels'], (dataForEvent[f'{self.tablename}_nEta'], dataForEvent[f'{self.tablename}_nPhi']))

        fig, ax = self.make_cmesh_plot(
            dataForEvent[f'{self.tablename}_nEta'], 
            dataForEvent[f'{self.tablename}_nPhi'], 
            pixels_2d,
            title=self._get_dataset_tag(self.datasetName)
            )
        
        ax.text(0,1,f'ievent={ievent}',
                fontsize=12,
                ha='left',
                va='bottom',
                transform=ax.transAxes
            )
    
        ax.text(1,1,self.pfType,
            fontsize=12,
            ha='right',
            va='bottom',
            transform=ax.transAxes
            )
    
        scatter_opts = {
            'marker' : 'x',
            'color' : "black",
            'linewidth' : 2,
        }
    
        ax.scatter(
            dataForEvent['jetEta'], 
            dataForEvent['jetPhi'], 
            label='GEN-matched jets',
            **scatter_opts
            )

        for iJet in range(len(dataForEvent['jetEta'])):
            loc = (dataForEvent['jetEta'][iJet], dataForEvent['jetPhi'][iJet])
            text = f'$p_T = {dataForEvent["jetPt"][iJet]:.2f} \\ GeV$'

            ax.annotate(text, loc, xytext=(loc[0], loc[1]+0.5), horizontalalignment='center')

        # Also plot the non-matching jets
        scatter_opts['color'] = 'red'
        ax.scatter(
            dataForEvent['nonMatchingJetEta'], 
            dataForEvent['nonMatchingJetPhi'], 
            label='Unmatched jets',
            **scatter_opts
            )

        ax.legend()

        # Draw a circle with R=0.4 around each jet
        circle_opts = {
            'fill' : False,
            'color': 'black',
            'radius' : 0.4,
            'linestyle' : '--',
            'linewidth' : 2.
        } 

        for jeteta, jetphi in zip(dataForEvent['jetEta'], dataForEvent['jetPhi']):
            circle = plt.Circle((jeteta, jetphi), **circle_opts)
            ax.add_patch(circle)

        circle_opts['color'] = 'red'
        for jeteta, jetphi in zip(dataForEvent['nonMatchingJetEta'], dataForEvent['nonMatchingJetPhi']):
            circle = plt.Circle((jeteta, jetphi), **circle_opts)
            ax.add_patch(circle)

        ax.set_ylim(-np.pi, np.pi)

        outfilename = f'{self.datasetName}_ievent_{ievent}_{self.pfType}.pdf'
        PlotSaver(fig, self.tag, self.jetsOnly).save(outfilename)

class RatioPlotMaker():
    def __init__(self, dfs, tag, pfType='all', jetsOnly=False) -> None:
        '''
        Plot the ratio of two event images for two different scenarios.
        (e.g. different cleaning cuts applied)
        '''
        self.dfs = dfs
        self.tag = tag
        # Type of PF candidate collection for the event image
        self.pfType = pfType
        # Only read the collection of PF candidates coming from jets?
        self.jetsOnly = jetsOnly
        self.tablename = "JetImage" if self.jetsOnly else "EventImage"

        self._read_data()

    def _read_data(self):
        branchname = f"{self.tablename}_{self.pfType}Pixels" if self.pfType != 'all' else f"{self.tablename}_pixels"

        # Assert that the two images are of the same size
        assert (self.dfs[0][f'{self.tablename}Size_nEtaBins'] == self.dfs[1][f'{self.tablename}Size_nEtaBins']).all()
        assert (self.dfs[0][f'{self.tablename}Size_nPhiBins'] == self.dfs[1][f'{self.tablename}Size_nPhiBins']).all()
        
        self.data = {
            'pixels0' : self.dfs[0][branchname],
            'pixels1' : self.dfs[1][branchname],
            'etaSize' : self.dfs[0][f'{self.tablename}Size_nEtaBins'],
            'phiSize' : self.dfs[0][f'{self.tablename}Size_nPhiBins'],
        }
    
    def make_ratio_plot(self, ievent):
        dataForEvent = {k: v[ievent] for k,v in self.data.items()}

        imshape = (dataForEvent['etaSize'], dataForEvent['phiSize'])
        pixels0_2d = np.reshape(dataForEvent['pixels0'], imshape)
        pixels1_2d = np.reshape(dataForEvent['pixels1'], imshape)

        etabins = np.linspace(-5, 5, dataForEvent['etaSize'])
        phibins = np.linspace(-np.pi, np.pi, dataForEvent['phiSize'])

        # Take the ratio and plot!
        ratio = pixels0_2d / pixels1_2d

        fig, ax = plt.subplots()
        cmap = ax.pcolormesh(etabins, phibins, ratio.T)
        cb = fig.colorbar(cmap, ax=ax)
        cb.set_label('Ratio of PF Energies')

        ax.set_xlabel('PF Candidate $\\eta$')
        ax.set_ylabel('PF Candidate $\\phi$')
        
        ax.text(0,1,f'ievent={ievent}',
                fontsize=14,
                ha='left',
                va='bottom',
                transform=ax.transAxes
            )
    
        ax.text(1,1,self.pfType,
            fontsize=14,
            ha='right',
            va='bottom',
            transform=ax.transAxes
            )
    
        outfilename = f'ievent_{ievent}_ratio_{self.pfType}.pdf'
        PlotSaver(fig, self.tag, self.jetsOnly).save(outfilename)

class AccumulationPlotMaker(ColormeshPlotter):
    def __init__(self, df, tag, dataset) -> None:
        super().__init__()
        self.df = df
        self.tag = tag
        self.dataset = dataset

        self._read_data()

        # Start with zero accumulator
        temp = self.data['pixels'].iloc[0]

        self.etaSize = self.data['etaSize'].iloc[0]
        self.phiSize = self.data['phiSize'].iloc[0]
        temp = np.reshape(temp, (self.etaSize, self.phiSize))

        self.accumulator = np.zeros_like(temp)

    def _read_data(self):
        self.data = {
            'pixels' : self.df['EventImage_pixels'],
            'etaSize' : self.df['EventImageSize_nEtaBins'],
            'phiSize' : self.df['EventImageSize_nPhiBins'],
        }

    def make_acc_plot(self, numevents=20):
        '''Make an image plot by accumulating numevents # of event images.'''
        for ievent in range(numevents):
            try:
                pixels = self.data['pixels'].iloc[ievent]
            except IndexError:
                print('Ran out of events, breaking out of loop.')
                print(f'Event: {ievent}')
                break
            
            # Reshape pixels
            pixels = np.reshape(pixels, (self.etaSize, self.phiSize))
            self.accumulator += pixels

        # Normalize to number of events we ran
        self.accumulator /= (ievent+1)
        
        fig, ax = self.make_cmesh_plot(self.etaSize, 
            self.phiSize, 
            self.accumulator, 
            title=self.dataset
            )

        ax.text(1,0,f'{ievent+1} events',
            ha='right',
            va='bottom',
            transform=ax.transAxes
        )

        outfilename=f'accumulated_{self.dataset}.pdf'
        PlotSaver(fig, self.tag).save(outfilename)