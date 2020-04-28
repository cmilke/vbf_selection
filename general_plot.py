import sys
import argparse
import pickle
import numpy
import itertools
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from uproot_methods import TLorentzVector as LV
from uproot_wrapper import event_iterator
from plotting_utils import plot_wrapper
import analysis_utils as autils

_cvv_vals = [0, 0.5, 1, 1.5, 2, 4]
_plots = plot_wrapper([])
    #'correlation'
  #, 'correlation_mjj' , 'correlation_eta' , 'correlation_sumpt'

_plots.add_hist1('resolved_pt', '$p_T$ Distribution of Resolved Jets',
        [''], 100, (0,200), xlabel='$p_T$ (GeV)', normalize=False)
_plots.add_hist1('resolved_eta', '$\eta$ Distribution of Resolved Jets',
        [''], 100, (-6,6), xlabel='\eta', normalize=False)
_plots.add_hist1('Deta_of_VBF_mjjmax', '$\Delta \eta$ Distribution of VBF Jets',
        [ cvv for cvv in _cvv_vals ],
        40, (2,10), xlabel='$\Delta \eta$', normalize=False, 
        labelmaker=lambda cvv:'$\kappa_{2V} = '+str(cvv)+'$' )
#_plots.add_hist1('truth_pt', '$p_T$ Distribution of Truth Jets',
#        [''], 100, (0,200), xlabel='$p_T$ (GeV)', normalize=False)
#_plots.add_hist1('truth_eta', '$\eta$ Distribution of Truth Jets',
#        [''], 100, (-6,6), xlabel='\eta', normalize=False)

_Nevents = 1000
_VBF_samples = {
    1: 'MC16d_VBF-HH-bbbb_cvv1'
}

_output_branches = [
    "run_number", "event_number", "mc_sf", "ntag", "njets",
    "n_VBF_candidates"
]

_branches = [
    #'ntruth',
    #('truth_particles', [
    #    'truth_pt',
    #    'truth_pdgId', 'truth_status', 'truth_is_higgs', 'truth_is_bhad'
    #]),
    #('truth_jets4', ['truthjet_antikt4_pt', 'truthjet_antikt4_eta']), #truth pt in MeV?
    'eventNumber', 'nresolvedJets',
    ('resolved_jets', [ 'resolvedJets_pt', 'resolvedJets_phi', 'resolvedJets_eta', 'resolvedJets_E',
        'resolvedJets_HadronConeExclTruthLabelID'

    ]) #resolved pt in GeV
]


make_reco_vector = lambda jet: LV.from_ptetaphie(jet['resolvedJets_pt'], jet['resolvedJets_eta'], jet['resolvedJets_phi'], jet['resolvedJets_E'])


def extract_data():
    for cvv_value, vbf_sample in _VBF_samples.items():
        print('\n\n\n')
        input_dataset  = autils.input_datasets[vbf_sample]
        output_dataset = autils.output_datasets[vbf_sample]


        selected_events = {}
        for output in event_iterator(output_dataset, 'VBF_tree', _output_branches, 100):#_Nevents):
            selected_events[output['event_number']] = 0
        print(selected_events)

        for event in event_iterator(input_dataset, 'XhhMiniNtuple', _branches, None):
            if event['eventNumber'] not in selected_events: continue
            print(event['eventNumber'])
            continue
            #for p in event['truth_particles']:
            #    print('            ',p['truth_pdgId'])
            num_reco = event['nresolvedJets']
            non_bjets = []
            for jet in event['resolved_jets']:
                _plots['resolved_pt'].fill(jet['resolvedJets_pt'])
                _plots['resolved_eta'].fill(jet['resolvedJets_eta'])
                if jet['resolvedJets_HadronConeExclTruthLabelID'] != 5:
                    non_bjets.append(make_reco_vector(jet))
            if len(non_bjets) > 1:
                deta_mjj_list = [ ( (i+j).mass, abs(i.eta - j.eta) ) for i,j in itertools.combinations(non_bjets, 2) ]
                deta_mjj_list.sort() # Sort by mjj
                filtered = [ (mass,Deta) for mass, Deta in deta_mjj_list if Deta > 3 ]
                if len(filtered) > 0: 
                    vbf_pair = filtered[0]
                    _plots['Deta_of_VBF_mjjmax'].fill(vbf_pair[1], cvv_value)


            #num_truth = 0
            #for jet in event['truth_jets4']:
            #    _plots['truth_pt'].fill(jet['truthjet_antikt4_pt']/1000)
            #    _plots['truth_eta'].fill(jet['truthjet_antikt4_eta'])
            #    if jet['truthjet_antikt4_pt'] > 25: num_truth += 1



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
