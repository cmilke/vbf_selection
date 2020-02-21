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
        'sig': autils.Flavntuple_list_VBFH125_gamgam_cmilkeV3[:1],
        'bgd': autils.Flavntuple_list_ggH125_gamgam_cmilkeV3[:1]
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
      , ('reco_jets',  ['j0truthid',  'j0pT', 'j0eta', 'j0phi', 'j0m',
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
    'EventWeight':None,
    'TruthJetID': [-5,40], 'TruthJetPt':[0,200], 'TruthJetEta':[-5,5], 'TruthJetPhi':None, 'TruthJetM':[0,40],
    'JetFlavor':[-5,40], 'JetPt_calib':[20,200], 'JetEta_calib':None, 'JetPhi_calib':None, 'JetM_calib':None,
    'JetPullMagnitude':[0,0.1], 'JetPullAngle':[-4,4],
    'JetTrkPt':[0,200], 'JetTrkM':[0,200],

    'Leading pt mass':[0,1000], 'Maximum $M_{jj}$':[0,1500],
    '$p_T$-Centrality':[-4,4], '$M_{jj}$-Centrality':[-4,4]
}


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




def load_cmilke(event_generator, input_type, validation_data):
    for event in event_generator:
        validation_data['EventWeight'][input_type].append(event['EventWeight'])
        init_jet_vectors = []
        for reco_jet in event['reco_jets']:
            if not reco_jet['JetJVT']: continue
            if reco_jet['JetPt_calib'] < 20: continue
            init_jet_vectors.append( TLorentzVector.from_ptetaphim(reco_jet['JetPt_calib'], reco_jet['JetEta_calib'], reco_jet['JetPhi_calib'], reco_jet['JetM_calib']) )

        #jet_vectors = [ v for v in init_jet_vectors if v.pt > 30 and abs(v.eta) < 4 ]
        jet_vectors = init_jet_vectors
        if len(jet_vectors) < 1: continue
        if jet_vectors[0].pt < 60: continue
        #if len(jet_vectors) > 1 and jet_vectors[1].pt < 60: continue

        #if len(jet_vectors) == 3:
        for v in jet_vectors:
            validation_data['JetPt_calib'][input_type].append(v.pt)
            validation_data['JetEta_calib'][input_type].append(v.eta)
            validation_data['JetPhi_calib'][input_type].append(v.phi)
            validation_data['JetM_calib'][input_type].append(v.mass)
            #load_extra(jet_vectors, input_type, validation_data)


_loaders = {'aviv':load_aviv, 'cmilke':load_cmilke, 'exp':load_cmilke}


def validate():
    ntuple_type = sys.argv[1]
    branch_list = _branch_options[ntuple_type]
    tree_name = _tree_options[ntuple_type]

    # Load data
    print('Loading...')
    branch_keys = unnest_list(branch_list, {}) + _extra_keys
    #input_keys = ['sig', 'bgd']
    input_keys = ['sig']
    validation_data = { b_key:{i_key:[] for i_key in input_keys} for b_key in branch_keys }
    for input_type in input_keys:
        input_list = _input_type_options[ntuple_type][input_type]
        event_generator = event_iterator(input_list, tree_name, branch_list, _Nevents)
        _loaders[ntuple_type](event_generator, input_type, validation_data)

    # Plot data
    print('Plotting...')
    output = PdfPages('plots_focussed_validation_'+ntuple_type+'.pdf')

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
