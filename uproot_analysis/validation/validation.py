#!/usr/bin/env python
import types
import sys
from itertools import combinations

from acorn_backend import analysis_utils as autils
from acorn_backend.uproot_wrapper import event_iterator, unnest_list
from uproot_methods import TLorentzVector

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

#Define all the high level root stuff: ntuple files, branches to be used
_Nevents = 10000
_hist_bins = 100

_input_type_options = {
    'aviv': {
        'sig': autils.Flavntuple_list_VBFH125_gamgam[:3],
        'bgd': autils.Flavntuple_list_ggH125_gamgam[:3]
    }

  , 'cmilke': {
        'sig': autils.Flavntuple_list_VBFH125_gamgam_cmilke[:1],
        'bgd': autils.Flavntuple_list_ggH125_gamgam_cmilke[:1]
    }
  , 'exp': {
        'sig': ['/nfs/slac/g/atlas/u02/cmilke/mc16-xAOD-ntuple-maker/run/sig_test/data-ANALYSIS/sample.root'],
        'bgd': ['/nfs/slac/g/atlas/u02/cmilke/mc16-xAOD-ntuple-maker/run/bgd_test/data-ANALYSIS/sample.root']
    }
}

_tree_options = {
    'aviv': 'Nominal'
  , 'cmilke': 'ntuple'
  , 'exp': 'ntuple'
}

_branch_options = {
    'aviv': [
        'eventWeight'
      , ('truth_particles', ['tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm'])
      , ('truth_jets', ['truthjpT', 'truthjeta', 'truthjphi', 'truthjm'])
      , ('reco_jets',  ['j0truthid',  'tj0pT', 'j0pT', 'j0eta', 'j0phi', 'j0m',
            'j0_isTightPhoton', 'j0_isLoosePhoton',
            'j0_JVT', 'j0_fJVT_Tight', 'j0_fJVT_Loose'
        ])
    ]

  , 'cmilke': [
        'EventWeight'
      , ('truth_jets', [ 'TruthJetPt', 'TruthJetEta', 'TruthJetPhi', 'TruthJetM', 'TruthJetID'] )
      , ('reco_jets', [ 'JetFlavor', 'JetPt_calib', 'JetEta_calib', 'JetPhi_calib', 'JetM_calib',
            'JetIsTightPhoton', 'JetIsLoosePhoton',
            'JetJVT', 'JetfJVT_tight', 'JetfJVT_loose',
            'JetScatterType', 'JetPullMagnitude', 'JetPullAngle',
            ('tracks', [ 'JetTrkPt', 'JetTrkEta', 'JetTrkPhi', 'JetTrkM' ])
        ])
    ]
}
_branch_options['exp'] = _branch_options['cmilke']

_extra_keys = [ 'Leading pt mass', 'Maximum $M_{jj}$', '$p_T$-Centrality', '$M_{jj}$-Centrality' ]

_xlimits = {
    'eventWeight':None,
    'truthjpT':[0,200], 'truthjeta':[-5,5], 'truthjphi':None, 'truthjm':[0,40],
    'j0truthid':[-5,40], 'j0pT':[0,200], 'j0eta':None, 'j0phi':None, 'j0m':None,

    'EventWeight':None,
    'TruthJetID': [-5,40], 'TruthJetPt':[0,200], 'TruthJetEta':[-5,5], 'TruthJetPhi':None, 'TruthJetM':[0,40],
    'JetFlavor':[-5,40], 'JetPt_calib':[0,200], 'JetEta_calib':None, 'JetPhi_calib':None, 'JetM_calib':None,
    'JetPullMagnitude':[0,0.1], 'JetPullAngle':[-4,4],
    'JetTrkPt':[0,200], 'JetTrkM':[0,200],

    'Leading pt mass':[0,1000], 'Maximum $M_{jj}$':[0,1500],
    '$p_T$-Centrality':[-4,4], '$M_{jj}$-Centrality':[-4,4]
}


def recursive_load(key, value, validation_data, input_type):
    if isinstance(value, types.GeneratorType):
        check_leading_jet_pt = True
        for entry in value:
            #try: # cmilke truth jets
            #    if entry['TruthJetPt'] < 20: continue
            #except KeyError: pass
            try: # cmilke reco jets
                if not entry['JetJVT']: continue
                #if entry['JetJVT']: continue
                #if entry['JetfJVT_tight']: continue

                if entry['JetPt_calib'] < 20: continue
                #if entry['JetPt_calib'] < 60: continue
            except KeyError: pass
            #try: # aviv reco jets
            #    if entry['j0pT'] < 30: continue
            #except KeyError: pass

            for subkey, subvalue in entry.items():
                recursive_load(subkey, subvalue, validation_data, input_type)
    else: validation_data[key][input_type].append(value)


def validate():
    ntuple_type = sys.argv[1]
    branch_list = _branch_options[ntuple_type]
    tree_name = _tree_options[ntuple_type]

    # Load data
    print('Loading...')
    branch_keys = unnest_list(branch_list, {}) #+ _extra_keys
    input_keys = ['sig', 'bgd']
    #input_keys = ['sig']
    validation_data = { b_key:{i_key:[] for i_key in input_keys} for b_key in branch_keys }
    for input_type in input_keys:
        input_list = _input_type_options[ntuple_type][input_type]
        event_generator = event_iterator(input_list, tree_name, branch_list, _Nevents)
        recursive_load(None, event_generator, validation_data, input_type)

    # Plot data
    print('Plotting...')
    output = PdfPages('plots_validation_'+ntuple_type+'.pdf')

    for plot_name, inputs in validation_data.items():
        plot_range = None if plot_name not in _xlimits else _xlimits[plot_name]
        plot_values = { 'x': [], 'label': [] }
        for input_type,data in inputs.items():
            plot_values['x'].append(data)
            plot_values['label'].append( input_type+' - '+str(len(data)) )
        fig,ax = plt.subplots()
        counts, bins, hist = plt.hist(**plot_values, histtype='step', linewidth=2, bins=_hist_bins, range=plot_range)
        ax.legend()
        plt.grid()
        plt.title(ntuple_type+': Distribution of '+plot_name+' Over '+str(_Nevents)+' Events')
        if plot_range != None: plt.xlim(*_xlimits[plot_name])
        output.savefig()
        plt.close()
    output.close()

validate()
