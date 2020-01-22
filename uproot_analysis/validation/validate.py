#!/usr/bin/env python

from acorn_backend import analysis_utils as autils
from acorn_backend.uproot_wrapper import event_iterator, unnest_list
from uproot_methods import TLorentzVector

import types
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

#Define all the high level root stuff: ntuple files, branches to be used
#_input_type_options = {
#    'sig': autils.Flavntuple_list_VBFH125_gamgam[:1],
#    'bgd': autils.Flavntuple_list_ggH125_gamgam[:1]
#}
_input_type_options = {
    'sig': ['/nfs/slac/g/atlas/u02/cmilke/mc16-xAOD-ntuple-maker/run/signal/data-ANALYSIS/sample.root'],
    'bgd': ['/nfs/slac/g/atlas/u02/cmilke/mc16-xAOD-ntuple-maker/run/background/data-ANALYSIS/sample.root']
}

_aviv_branch_list = [
    'eventWeight',
    ('truth_particles',  ['tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm']),
    ('truth_jets', ['truthjpT', 'truthjeta', 'truthjphi', 'truthjm']),
    ('reco_jets',  ['tj0pT', 'j0truthid', 'j0_isTightPhoton', 'j0_isPU', 
                        'j0_JVT', 'j0_fJVT_Loose', 'j0_fJVT_Tight', 'j0pT', 'j0eta', 'j0phi', 'j0m'])
]

_cmilkeV1_branch_list = [
    'EventWeight',
    ('truth_jets', [
        'TruthJetPt', 'TruthJetEta', 'TruthJetPhi', 'TruthJetM', 'TruthJetID'
    ]),
    ('reco_jets', [
        'JetE_constit', 'JetPt_constit', 'JetEta_constit', 'JetPhi_constit', 'JetM_constit',
        'JetE_calib', 'JetPt_calib', 'JetEta_calib', 'JetPhi_calib', 'JetM_calib',
        'JetTiming', 'JetNegE', 'JetCharge', 'JetAngularity', 'JetFlavor', 'JetScatterType', 'JetMatchIndex',
        ('tracks', [
            'JetTrkPt', 'JetTrkEta', 'JetTrkPhi', 'JetTrkZ0', 'JetTrkD0', 'JetTrkZ0err',
            'JetTrkD0err'
        ])
    ])
]



#_Nevents = 10000
#_Nevents = None
_Nevents = 10000
_hist_bins = 100


def recursive_load(key, value, validation_data, input_type):
    if isinstance(value, types.GeneratorType):
        for entry in value:
            for subkey, subvalue in entry.items():
                recursive_load(subkey, subvalue, validation_data, input_type)
    else: validation_data[key][input_type].append(value)


def validate():
    #branch_list = _aviv_branch_list
    #tree_name = 'Nominal'
    branch_list = _cmilkeV1_branch_list
    tree_name = 'ntuple'

    # Load data
    branch_keys = unnest_list(branch_list, {})
    input_keys = ['sig', 'bgd']
    validation_data = { b_key:{i_key:[] for i_key in input_keys} for b_key in branch_keys }
    for input_type in input_keys:
        input_list = _input_type_options[input_type]
        event_generator = event_iterator(input_list, tree_name, branch_list, _Nevents)
        recursive_load(None, event_generator, validation_data, input_type)


    # Plot data
    output = PdfPages('plots_validation.pdf')

    for plot_name, inputs in validation_data.items():
        plot_values = { 'x': [], 'label': [] }
        for input_type,data in inputs.items():
            plot_values['x'].append(data)
            plot_values['label'].append( input_type+' - '+str(len(data)) )

        fig,ax = plt.subplots()
        counts, bins, hist = plt.hist(**plot_values, histtype='step', linewidth=2, bins=_hist_bins)
        ax.legend()
        plt.grid()
        plt.title('Distribution of '+plot_name+' Over '+str(_Nevents)+' Events')
        output.savefig()
        plt.close()
    output.close()

validate()
