#!/usr/bin/env python
import types
import sys

from acorn_backend import analysis_utils as autils
from acorn_backend.uproot_wrapper import event_iterator, unnest_list
from uproot_methods import TLorentzVector

#Define all the high level root stuff: ntuple files, branches to be used
_Nevents = 100000

_input_type_options = {
    'aviv': {
        'sig': autils.Flavntuple_list_VBFH125_gamgam[:3],
        'bgd': autils.Flavntuple_list_ggH125_gamgam[:3]
    }

  , 'cmilke': {
        'sig': autils.Flavntuple_list_VBFH125_gamgam_cmilke[:1],
        'bgd': autils.Flavntuple_list_ggH125_gamgam_cmilke[:1]
    }
}

_tree_options = {
    'aviv': 'Nominal'
  , 'cmilke': 'ntuple'
}

_branch_options = {
    'aviv': [
        'eventWeight'
      , ('truth_particles', ['tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm'])
      #, ('truth_jets', ['truthjpT', 'truthjeta', 'truthjphi', 'truthjm'])
      , ('reco_jets',  ['j0truthid',  'j0pT', 'j0eta', 'j0phi', 'j0m'])
    ]

  , 'cmilke': [
        'EventWeight'
      #, ('truth_jets', [ 'TruthJetPt', 'TruthJetEta', 'TruthJetPhi', 'TruthJetM'] )
      , ('reco_jets', [ 'JetFlavor', 'JetPt_calib', 'JetEta_calib', 'JetPhi_calib', 'JetM_calib',
                        'JetJVT', 'JetfJVT_tight'] )
    ]
}


def load_aviv(event_generator):
    counts = {}
    for index, event in enumerate(event_generator): pass
        #for p in event['truth_particles']:
        #    #print( '{:.02}, {:.02}, {:.02}, {:.02}'.format(p['tpartpT'], p['tparteta'], p['tpartphi'], p['tpartm']) )
        #    tag = (p['tpartpdgID'], p['tpartstatus'])
        #    if tag not in counts: counts[tag] = 0
        #    counts[tag] += 1


def load_cmilke(event_generator):
    num_2_jets = 0
    num_3_jets = 0
    for event in event_generator:
        #print('\n'+str(event['EventWeight']))

        #for truth_jet in event['truth_jets']:
        #    print( '{:.02}, {:.02}, {:.02}, {:.02}'.format(truth_jet['TruthJetPt'], truth_jet['TruthJetEta'], truth_jet['TruthJetPhi'], truth_jet['TruthJetM']) )
        num_jets = 0
        num_quarks = 0
        pt_list = []
        for jet in event['reco_jets']:
            if jet['JetFlavor'] == autils.PDGID['photon']: continue
            if abs(jet['JetEta_calib']) > 4: continue
            if jet['JetPt_calib'] < 30: continue
            if not (jet['JetJVT'] and jet['JetfJVT_tight']): continue
            if jet['JetFlavor'] in autils.PDGID['quarks']: num_quarks += 1
            pt_list.append(jet['JetPt_calib'])
            num_jets += 1
        if num_jets > 1:
            if num_quarks < 2: continue
            if pt_list[0] < 70: continue
            if pt_list[1] < 50: continue
            if num_jets == 2: num_2_jets += 1
            if num_jets == 3: num_3_jets += 1
    all_jets = num_2_jets + num_3_jets
    print( '{}, {}, {}, {:.02f}, {:.02f}'.format(all_jets, num_2_jets, num_3_jets, num_2_jets/all_jets, num_3_jets/all_jets) )



_loaders = {'aviv':load_aviv, 'cmilke':load_cmilke}


def validate():
    ntuple_type = sys.argv[1]
    input_type = 'sig'
    branch_list = _branch_options[ntuple_type]
    tree_name = _tree_options[ntuple_type]

    # Load data
    input_list = _input_type_options[ntuple_type][input_type]
    print('\n\nLoading '+ntuple_type+'...')
    _loaders[ntuple_type]( event_iterator(input_list, tree_name, branch_list, _Nevents) )


validate()
