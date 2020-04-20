#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import sys
import argparse
import pickle
import numpy
import itertools
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from uproot_wrapper import event_iterator
from plotting_utils import plot_wrapper
import analysis_utils as autils

_plots = plot_wrapper([])
    #'correlation'
  #, 'correlation_mjj' , 'correlation_eta' , 'correlation_sumpt'

_plots.add_hist1('resolved_pt', '$p_T$ Distribution of Resolved Jets',
        [''], 100, (0,200), xlabel='$p_T$ (GeV)', normalize=False)
_plots.add_hist1('truth_pt', '$p_T$ Distribution of Truth Jets',
        [''], 100, (0,200), xlabel='$p_T$ (GeV)', normalize=False)
_plots.add_hist1('resolved_eta', '$\eta$ Distribution of Resolved Jets',
        [''], 100, (-6,6), xlabel='\eta', normalize=False)
_plots.add_hist1('truth_eta', '$\eta$ Distribution of Truth Jets',
        [''], 100, (-6,6), xlabel='\eta', normalize=False)

_Nevents = 1000
_input_list = autils.datasets['MC16d_VBF-HH-bbbb_cvv1']
#_input_list = autils.datasets['MC16d_ggF-HH-bbbb']
_tree_name = 'XhhMiniNtuple'
_branches = [
    'ntruth',
    ('truth_particles', [
        'truth_pt',
        'truth_pdgId', 'truth_status', 'truth_is_higgs', 'truth_is_bhad'
    ]),
    ('truth_jets4', ['truthjet_antikt4_pt', 'truthjet_antikt4_eta']), #truth pt in MeV?
    'nresolvedJets',
    ('resolved_jets', [ 'resolvedJets_pt', 'resolvedJets_phi', 'resolvedJets_eta']) #resolved pt in GeV
]


def extract_data():
    counts = [0]*20
    for event in event_iterator(_input_list, _tree_name, _branches, _Nevents):
        #for p in event['truth_particles']:
        #    print('            ',p['truth_pdgId'])
        num_reco = event['nresolvedJets']
        counts[num_reco] += 1
        for jet in event['resolved_jets']:
            _plots['resolved_pt'].fill(jet['resolvedJets_pt'])
            _plots['resolved_eta'].fill(jet['resolvedJets_eta'])

        num_truth = 0
        for jet in event['truth_jets4']:
            _plots['truth_pt'].fill(jet['truthjet_antikt4_pt']/1000)
            _plots['truth_eta'].fill(jet['truthjet_antikt4_eta'])
            if jet['truthjet_antikt4_pt'] > 25: num_truth += 1

    print(counts)



    

def draw_distributions():
    parser = argparse.ArgumentParser()
    parser.add_argument( "-r", required = False, default = False, action = 'store_true', help = "Refresh cache",) 
    parser.add_argument( "-p", required = False, default = False, action = 'store_true', help = "Print only, do not plot",) 
    args = parser.parse_args()

    refresh = args.r
    cache = {}
    cache_file = '.cache/general_plots.p'
    if refresh: extract_data()
    else: cache = pickle.load( open(cache_file, 'rb') )
    if not args.p:
        print('Data extracted, plotting...')
        _plots.plot_all(refresh, cache)
        if refresh: pickle.dump( cache, open(cache_file, 'wb') )

draw_distributions()
