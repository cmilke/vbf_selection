#!/usr/bin/env python
import types
import sys

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

  , 'cmilkeV1': {
        'sig': ['/nfs/slac/g/atlas/u02/cmilke/mc16-xAOD-ntuple-maker/run/signal/data-ANALYSIS/sample.root'],
        'bgd': ['/nfs/slac/g/atlas/u02/cmilke/mc16-xAOD-ntuple-maker/run/background/data-ANALYSIS/sample.root']
    }
}

_tree_options = {
    'aviv': 'Nominal'
  , 'cmilkeV1': 'ntuple'
}

#_branch_options = {
#    'aviv': [
#        'eventWeight',
#        ('truth_particles',  ['tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm']),
#        ('truth_jets', ['truthjpT', 'truthjeta', 'truthjphi', 'truthjm']),
#        ('reco_jets',  ['tj0pT', 'j0truthid', 'j0_isTightPhoton', 'j0_isPU', 
#                            'j0_JVT', 'j0_fJVT_Loose', 'j0_fJVT_Tight', 'j0pT', 'j0eta', 'j0phi', 'j0m'])
#    ]
#
#  , 'cmilkeV1': [
#        'EventWeight',
#        ('truth_jets', [
#            'TruthJetPt', 'TruthJetEta', 'TruthJetPhi', 'TruthJetM', 'TruthJetID'
#        ]),
#        ('reco_jets', [
#            'JetE_constit', 'JetPt_constit', 'JetEta_constit', 'JetPhi_constit', 'JetM_constit',
#            'JetE_calib', 'JetPt_calib', 'JetEta_calib', 'JetPhi_calib', 'JetM_calib',
#            'JetTiming', 'JetNegE', 'JetCharge', 'JetAngularity', 'JetFlavor', 'JetScatterType', 'JetMatchIndex',
#            ('tracks', [
#                'JetTrkPt', 'JetTrkEta', 'JetTrkPhi', 'JetTrkZ0', 'JetTrkD0', 'JetTrkZ0err',
#                'JetTrkD0err'
#            ])
#        ])
#    ]
#}
_branch_options = {
    'aviv': [
        'eventWeight'
      , ('truth_jets', ['truthjpT', 'truthjeta', 'truthjphi', 'truthjm'])
      #, ('reco_jets',  ['j0truthid',  'j0pT', 'j0eta', 'j0phi', 'j0m'])
    ]

  , 'cmilkeV1': [
        'EventWeight'
      , ('truth_jets', [ 'TruthJetPt', 'TruthJetEta', 'TruthJetPhi', 'TruthJetM'] )
      #, ('reco_jets', [ 'JetFlavor', 'JetPt_calib', 'JetEta_calib', 'JetPhi_calib', 'JetM_calib'] )
    ]
}

_extra_keys = [ 'Leading pt mass' ]

_xlimits = {
    'eventWeight':None,
    'truthjpT':[0,200], 'truthjeta':[-5,5], 'truthjphi':None, 'truthjm':[0,40],
    'j0truthid':[-5,40], 'j0pT':[20,200], 'j0eta':None, 'j0phi':None, 'j0m':None,

    'EventWeight':None,
    'TruthJetPt':[0,200], 'TruthJetEta':[-5,5], 'TruthJetPhi':None, 'TruthJetM':[0,40],
    'JetFlavor':[-5,40], 'JetPt_calib':[20,200], 'JetEta_calib':None, 'JetPhi_calib':None, 'JetM_calib':None
}


def load_aviv(event_generator, input_type, validation_data):
    for event in event_generator:
        validation_data['eventWeight'][input_type].append(event['eventWeight'])

        init_jet_vectors = []
        for truth_jet in event['truth_jets']:
            init_jet_vectors.append( TLorentzVector.from_ptetaphim(truth_jet['truthjpT'], truth_jet['truthjeta'], truth_jet['truthjphi'], truth_jet['truthjm']) )

        jet_vectors = [ v for v in init_jet_vectors if v.pt > 20 ]

        if len(jet_vectors) > 2:
            for v in jet_vectors:
                validation_data['truthjpT'][input_type].append(v.pt)
                validation_data['truthjeta'][input_type].append(v.eta)
                validation_data['truthjphi'][input_type].append(v.phi)
                validation_data['truthjm'][input_type].append(v.mass)

            jet_vectors.sort(key=lambda v: v.pt, reverse=True)
            leading_pt_mass = (jet_vectors[0] + jet_vectors[1]).mass
            validation_data['Leading pt mass'][input_type].append(leading_pt_mass)


def load_cmilkeV1(event_generator, input_type, validation_data):
    for event in event_generator:
        validation_data['EventWeight'][input_type].append(event['EventWeight'])

        init_jet_vectors = []
        for truth_jet in event['truth_jets']:
            init_jet_vectors.append( TLorentzVector.from_ptetaphim(truth_jet['TruthJetPt'], truth_jet['TruthJetEta'], truth_jet['TruthJetPhi'], truth_jet['TruthJetM']) )

        jet_vectors = [ v for v in init_jet_vectors if v.pt > 20 ]

        if len(jet_vectors) > 2:
            for v in jet_vectors:
                validation_data['TruthJetPt'][input_type].append(v.pt)
                validation_data['TruthJetEta'][input_type].append(v.eta)
                validation_data['TruthJetPhi'][input_type].append(v.phi)
                validation_data['TruthJetM'][input_type].append(v.mass)

            jet_vectors.sort(key=lambda v: v.pt, reverse=True)
            leading_pt_mass = (jet_vectors[0] + jet_vectors[1]).mass
            validation_data['Leading pt mass'][input_type].append(leading_pt_mass)


_loaders = {'aviv':load_aviv, 'cmilkeV1':load_cmilkeV1}


def recursive_load(key, value, validation_data, input_type):
    if isinstance(value, types.GeneratorType):
        for entry in value:
            for subkey, subvalue in entry.items():
                recursive_load(subkey, subvalue, validation_data, input_type)
    else: validation_data[key][input_type].append(value)


def validate():
    ntuple_type = sys.argv[1]
    branch_list = _branch_options[ntuple_type]
    tree_name = _tree_options[ntuple_type]

    # Load data
    print('Loading...')
    branch_keys = unnest_list(branch_list, {}) + _extra_keys
    input_keys = ['sig', 'bgd']
    validation_data = { b_key:{i_key:[] for i_key in input_keys} for b_key in branch_keys }
    for input_type in input_keys:
        input_list = _input_type_options[ntuple_type][input_type]
        event_generator = event_iterator(input_list, tree_name, branch_list, _Nevents)
        #recursive_load(None, event_generator, validation_data, input_type)
        _loaders[ntuple_type](event_generator, input_type, validation_data)



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
