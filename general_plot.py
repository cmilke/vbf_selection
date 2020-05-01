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
from tagger_methods import Tagger_options as Tag
from plotting_utils import plot_wrapper
import analysis_utils as autils

#_cvv_vals = [0, 0.5, 1, 1.5, 2, 4]
_cvv_vals = [1]
_blacklist = ['Deta_of_VBF_mjjmax_mass']
#_blacklist = []
_plots = plot_wrapper(_blacklist)

_plots.add_hist1('pt', '$p_T$ Distribution of VBF Candidate Jets',
        [''], 100, (0,200), xlabel='$p_T$ (GeV)', normalize=False)
_plots.add_hist1('eta', '$\eta$ Distribution of VBF Candidate Jets',
        [''], 100, (-6,6), xlabel='$\eta$', normalize=False)

for mass in [0, 1000]:
    _plots.add_hist1(f'Deta_of_VBF_mjjmax_mass{mass}', '$\Delta \eta$ Distribution of VBF Jets w/ $M_{jj}>$'f'{mass} GeV',
            [ cvv for cvv in _cvv_vals ],
            40, (0,10), xlabel='$\Delta \eta$', normalize=False, 
            labelmaker=lambda cvv:'$\kappa_{2V} = '+str(cvv)+'$' )

_taggers = ['mjjmax', 'Deta3_mjjmax', 'mjN']
_plots.add_roc('rocs', 'Efficiency/Rejection Performance of Various VBF/ggF Discriminators', _taggers, zooms=[((0,1),(0.8,1))])
#_plots.add_roc('rocs_bare', 'Efficiency/Rejection Performance of Various VBF/ggF Discriminators,\nWithout Normalization', roc_curves, normalize=False)
_plots['rocs'].add_marker('Deta3_mjjmax', 1000, annotation='1000 GeV', marker='*', color='red')


_Nevents = 10000
_VBF_samples = { cvv_val:sample for cvv_val, sample in zip(_cvv_vals, autils.sample_list[1:]) }

_output_branches = [
    'run_number', 'event_number', 'mc_sf', 'ntag', 'njets',
    'n_vbf_candidates',
    ('jets', ['vbf_candidates_E', 'vbf_candidates_pT', 'vbf_candidates_eta', 'vbf_candidates_phi'])

]


make_reco_vector = lambda jet: LV.from_ptetaphie(jet['resolvedJets_pt'], jet['resolvedJets_eta'], jet['resolvedJets_phi'], jet['resolvedJets_E'])
make_nano_vector = lambda jet: LV.from_ptetaphie(jet['vbf_candidates_pT'], jet['vbf_candidates_eta'], jet['vbf_candidates_phi'], jet['vbf_candidates_E'])


def process_events(events, bgd=False, cvv_value=-1):
    num_jets = [0]*20
    for event in events:
        weight = event['mc_sf'][0]
        vecs = [ make_nano_vector(jet) for jet in event['jets'] ]
        num_jets[len(vecs)] += 1

        if len(vecs) > 1 and (cvv_value == 1 or bgd):
            for tagger in _taggers: _plots['rocs'].fill( Tag[tagger](vecs), bgd, tagger)
            #_plots['rocs_bare'].fill( Tagger[tag](vecs), bgd, tag, weight=weight)

        if not bgd and len(vecs) > 1:
            deta_mjj_list = [ ( (i+j).mass, abs(i.eta - j.eta) ) for i,j in itertools.combinations(vecs, 2) ]
            deta_mjj_list.sort() # Sort by mjj
            Deta_filtered = [ (mass,Deta) for mass, Deta in deta_mjj_list ] #if Deta > 3 ]
            for mass in [0,1000]:
                mass_filtered = [ pair for pair in Deta_filtered if pair[0] > mass ]
                if len(mass_filtered) > 0: 
                    vbf_pair = mass_filtered[0]
                    _plots[f'Deta_of_VBF_mjjmax_mass{mass}'].fill(vbf_pair[1], cvv_value)

        if cvv_value == 1:
            for v in vecs:
                _plots['pt'].fill(v.pt)
                _plots['eta'].fill(v.eta)
    jet_counts = numpy.array(num_jets[2:10])
    #print(jet_counts)
    #for count,frac in enumerate(jet_counts/jet_counts.sum()): print(f'{count+2}: {frac*100:4.1f}')



def extract_data():
    for cvv_value, vbf_sample in _VBF_samples.items():
        sig_events = event_iterator(autils.output_datasets[vbf_sample], 'VBF_tree', _output_branches, _Nevents)
        process_events(sig_events, cvv_value=cvv_value)

    bgd_events = event_iterator(autils.output_datasets['MC16d_ggF-HH-bbbb'], 'VBF_tree', _output_branches, _Nevents)
    process_events(bgd_events, bgd=True)



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
