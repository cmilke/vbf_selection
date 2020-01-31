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
_Nevents = 100000
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
      , ('truth_particles', ['tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm'])
      , ('truth_jets', ['truthjpT', 'truthjeta', 'truthjphi', 'truthjm'])
      #, ('reco_jets',  ['j0truthid',  'j0pT', 'j0eta', 'j0phi', 'j0m'])
    ]

  , 'cmilkeV1': [
        'EventWeight'
      , ('truth_jets', [ 'TruthJetPt', 'TruthJetEta', 'TruthJetPhi', 'TruthJetM', 'TruthJetID'] )
      #, ('reco_jets', [ 'JetFlavor', 'JetPt_calib', 'JetEta_calib', 'JetPhi_calib', 'JetM_calib'] )
    ]
}

_extra_keys = [ 'Leading pt mass', 'Maximum $M_{jj}$', '$p_T$-Centrality', '$M_{jj}$-Centrality' ]

_xlimits = {
    'eventWeight':None,
    'truthjpT':[0,200], 'truthjeta':[-5,5], 'truthjphi':None, 'truthjm':[0,40],
    'j0truthid':[-5,40], 'j0pT':[20,200], 'j0eta':None, 'j0phi':None, 'j0m':None,

    'EventWeight':None,
    'TruthJetPt':[0,200], 'TruthJetEta':[-5,5], 'TruthJetPhi':None, 'TruthJetM':[0,40],
    'JetFlavor':[-5,40], 'JetPt_calib':[20,200], 'JetEta_calib':None, 'JetPhi_calib':None, 'JetM_calib':None,

    'Leading pt mass':[0,1000], 'Maximum $M_{jj}$':[0,1500],
    '$p_T$-Centrality':[-4,4], '$M_{jj}$-Centrality':[-4,4]
}

def match_aviv_reco_jet0(vector_to_match, truth_particles):
    for tp in truth_particles:
        if tp['tpartpdgID'] == autils.PDGID['photon']:
            if tp['tpartstatus'] != autils.Status['photon_out']: continue
        elif tp['tpartstatus'] != autils.Status['outgoing']: continue

        truth_vec = TLorentzVector.from_ptetaphim(tp['tpartpT'], tp['tparteta'], tp['tpartphi'], tp['tpartm'])
        deltaR = vector_to_match.delta_r(truth_vec)
        if deltaR < 0.3: return tp['tpartpdgID']
    return -1


def match_aviv_reco_jet1(vector_to_match, truth_particles):
    max_pt = 0
    max_pt_pdgid = -1
    for tp in truth_particles:
        if tp['tpartpdgID'] == autils.PDGID['photon']:
            if tp['tpartstatus'] != autils.Status['photon_out']: continue
        elif tp['tpartstatus'] != autils.Status['outgoing']: continue

        truth_vec = TLorentzVector.from_ptetaphim(tp['tpartpT'], tp['tparteta'], tp['tpartphi'], tp['tpartm'])
        deltaR = vector_to_match.delta_r(truth_vec)
        if deltaR < 0.3 and truth_vec.pt > max_pt:
            max_pt = truth_vec.pt
            max_pt_pdgid = tp['tpartpdgID']
    return max_pt_pdgid


def match_aviv_reco_jet2(vector_to_match, truth_particles):
    for tp in truth_particles:
        if tp['tpartstatus'] not in (autils.Status['outgoing'], autils.Status['photon_out']): continue

        truth_vec = TLorentzVector.from_ptetaphim(tp['tpartpT'], tp['tparteta'], tp['tpartphi'], tp['tpartm'])
        deltaR = vector_to_match.delta_r(truth_vec)
        if deltaR < 0.3: return tp['tpartpdgID']
    return -1


def match_aviv_reco_jet3(vector_to_match, truth_particles):
    max_pt = 0
    max_pt_pdgid = -1
    for tp in truth_particles:
        if tp['tpartpdgID'] == autils.PDGID['higgs']: continue

        truth_vec = TLorentzVector.from_ptetaphim(tp['tpartpT'], tp['tparteta'], tp['tpartphi'], tp['tpartm'])
        deltaR = vector_to_match.delta_r(truth_vec)
        if deltaR < 0.3 and truth_vec.pt > max_pt:
            max_pt = truth_vec.pt
            max_pt_pdgid = tp['tpartpdgID']
    return max_pt_pdgid


def match_aviv_reco_jet(vector_to_match, truth_particles):
    max_pt = 0
    max_pt_pdgid = -1
    for tp in truth_particles:
        if tp['tpartstatus'] not in (autils.Status['outgoing'], autils.Status['photon_out']): continue

        truth_vec = TLorentzVector.from_ptetaphim(tp['tpartpT'], tp['tparteta'], tp['tpartphi'], tp['tpartm'])
        deltaR = vector_to_match.delta_r(truth_vec)
        if deltaR < 0.3 and truth_vec.pt > max_pt:
            max_pt = truth_vec.pt
            max_pt_pdgid = tp['tpartpdgID']
    return max_pt_pdgid


def load_extra(jet_vectors, input_type, validation_data):
    jet_vectors.sort(key=lambda v: v.pt, reverse=True)
    leading_pt_mass = (jet_vectors[0] + jet_vectors[1]).mass
    validation_data['Leading pt mass'][input_type].append(leading_pt_mass)

    primaries = sorted(jet_vectors[:2], key=lambda v: v.eta)
    centrality_pt = 2*(jet_vectors[2].eta - primaries[0].eta) / ( primaries[1].eta - primaries[0].eta ) - 1
    validation_data['$p_T$-Centrality'][input_type].append(centrality_pt)

    mass_pairs = [ ( (i+j).mass, i,j,k ) for i,j in combinations(jet_vectors, 2) for k in jet_vectors if k not in (i,j) ]
    mass_pairs.sort(reverse=True, key=lambda t: t[0])
    mjj_pair = mass_pairs[0]
    primaries = sorted(mjj_pair[1:3], key=lambda v: v.eta)
    validation_data['Maximum $M_{jj}$'][input_type].append(mjj_pair[0])
    centrality_mjj = 2*(mjj_pair[3].eta - primaries[0].eta) / ( primaries[1].eta - primaries[0].eta ) - 1
    validation_data['$M_{jj}$-Centrality'][input_type].append(centrality_mjj)


def load_aviv(event_generator, input_type, validation_data):
    for event in event_generator:
        validation_data['eventWeight'][input_type].append(event['eventWeight'])

        truth_particles = [ tp.copy() for tp in event['truth_particles'] ]

        init_jet_vectors = []
        for truth_jet in event['truth_jets']:
            v = TLorentzVector.from_ptetaphim(truth_jet['truthjpT'], truth_jet['truthjeta'], truth_jet['truthjphi'], truth_jet['truthjm']) 
            pdgid = match_aviv_reco_jet3(v, truth_particles)
            if pdgid == autils.PDGID['photon']: continue
            init_jet_vectors.append(v)

        jet_vectors = [ v for v in init_jet_vectors if v.pt > 20 and abs(v.eta) < 4 ]

        if len(jet_vectors) == 3:
            for v in jet_vectors:
                validation_data['truthjpT'][input_type].append(v.pt)
                validation_data['truthjeta'][input_type].append(v.eta)
                validation_data['truthjphi'][input_type].append(v.phi)
                validation_data['truthjm'][input_type].append(v.mass)
            load_extra(jet_vectors, input_type, validation_data)




def load_cmilkeV1(event_generator, input_type, validation_data):
    for event in event_generator:
        validation_data['EventWeight'][input_type].append(event['EventWeight'])

        init_jet_vectors = []
        for truth_jet in event['truth_jets']:
            if truth_jet['TruthJetID'] == autils.PDGID['photon']: continue
            init_jet_vectors.append( TLorentzVector.from_ptetaphim(truth_jet['TruthJetPt'], truth_jet['TruthJetEta'], truth_jet['TruthJetPhi'], truth_jet['TruthJetM']) )

        jet_vectors = [ v for v in init_jet_vectors if v.pt > 20 and abs(v.eta) < 4 ]

        if len(jet_vectors) == 3:
            for v in jet_vectors:
                validation_data['TruthJetPt'][input_type].append(v.pt)
                validation_data['TruthJetEta'][input_type].append(v.eta)
                validation_data['TruthJetPhi'][input_type].append(v.phi)
                validation_data['TruthJetM'][input_type].append(v.mass)
            load_extra(jet_vectors, input_type, validation_data)


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
