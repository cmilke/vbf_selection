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

  , 'cmilkeV1': {
        'sig': ['/nfs/slac/g/atlas/u02/cmilke/mc16-xAOD-ntuple-maker/run/signal/data-ANALYSIS/sample.root'],
        'bgd': ['/nfs/slac/g/atlas/u02/cmilke/mc16-xAOD-ntuple-maker/run/background/data-ANALYSIS/sample.root']
    }
}

_tree_options = {
    'aviv': 'Nominal'
  , 'cmilkeV1': 'ntuple'
}

_branch_options = {
    'aviv': [
        'eventWeight'
      , ('truth_particles', ['tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm'])
      , ('truth_jets', ['truthjpT', 'truthjeta', 'truthjphi', 'truthjm'])
      #, ('reco_jets',  ['j0truthid',  'j0pT', 'j0eta', 'j0phi', 'j0m'])
    ]

  , 'cmilkeV1': [
        'EventWeight'
      , ('truth_jets', [ 'TruthJetPt', 'TruthJetEta', 'TruthJetPhi', 'TruthJetM'] )
      #, ('reco_jets', [ 'JetFlavor', 'JetPt_calib', 'JetEta_calib', 'JetPhi_calib', 'JetM_calib'] )
    ]
}


def load_aviv(event_generator):
    counts = {}
    for index, event in enumerate(event_generator):
        #maybe_sorted = [ (p['tpartpdgID'], p['tpartpT']) for p in event['truth_particles'] if p['tpartpdgID'] != 25 ]
        #def_sorted = sorted(maybe_sorted, reverse=True)
        #print(maybe_sorted)#, def_sorted)
        #if maybe_sorted != def_sorted: count += 1
        #if index % 1000 == 0: print(index)


        #    if p['tpartpdgID'] == autils.PDGID['photon']:
        #        status = p['tpartstatus']
        #        if status not in counts: counts[status] = 0
        #        counts[status] += 1
        for p in event['truth_particles']:
            #print( '{:.02}, {:.02}, {:.02}, {:.02}'.format(p['tpartpT'], p['tparteta'], p['tpartphi'], p['tpartm']) )
            tag = (p['tpartpdgID'], p['tpartstatus'])
            if tag not in counts: counts[tag] = 0
            counts[tag] += 1
    #print('FINAL TALLY: '+str(count) )
    keys = sorted(list(counts), key=lambda t:t[0])
    for key in keys: print( str(key) + ': '+str(counts[key]))

        #print('\n'+str(event['eventWeight']))

        #for truth_jet in event['truth_jets']:
        #    print( '{:.02}, {:.02}, {:.02}, {:.02}'.format(truth_jet['truthjpT'], truth_jet['truthjeta'], truth_jet['truthjphi'], truth_jet['truthjm']) )


def load_cmilkeV1(event_generator):
    for event in event_generator:
        print('\n'+str(event['EventWeight']))

        for truth_jet in event['truth_jets']:
            print( '{:.02}, {:.02}, {:.02}, {:.02}'.format(truth_jet['TruthJetPt'], truth_jet['TruthJetEta'], truth_jet['TruthJetPhi'], truth_jet['TruthJetM']) )



_loaders = {'aviv':load_aviv, 'cmilkeV1':load_cmilkeV1}


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
