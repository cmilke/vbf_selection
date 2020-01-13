#!/usr/bin/env python

from acorn_backend import analysis_utils as autils
from acorn_backend.uproot_wrapper import event_iterator
import uproot

#Define all the high level root stuff: ntuple files, branches to be used
_input_type_options = {
    'sig': autils.Flavntuple_list_VBFH125_gamgam,
    'bgd': autils.Flavntuple_list_ggH125_gamgam[:1]
}
#input_list = ['/nfs/slac/g/atlas/u02/cmilke/mc16-xAOD-ntuple-maker/run/submitDir/data-ANALYSIS/sample.root']

_branch_list = [
    'eventWeight',
    ('truth_particles',  ['tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm']),
    ('truth_jets', ['truthjpT', 'truthjeta', 'truthjphi', 'truthjm']),
    ('reco_jets',  ['tj0pT', 'j0truthid', 'j0_isTightPhoton', 'j0_isPU', 
                        'j0_JVT', 'j0_fJVT_Loose', 'j0_fJVT_Tight', 'j0pT', 'j0eta', 'j0phi', 'j0m'])
]

#_branch_list = [
#    'RunNumber',
#    'EventNumber',
#    'EventWeight',
#    'MU',
##    ('truth_particles', [
##        'TpartpdgID',
##        'Tpartstatus',
##        'TpartE',
##        'TpartPt',
##        'TpartEta',
##        'TpartPhi',
##        'TpartM'
##    ]),
#    ('reco_jets', [
#        'JetFlavor',
#        'JetPt_calib',
#        'JetScatterType',
#        ('reco_tracks', [
#            'JetTrkPt',
#            'JetTrkEta'
#        ])
#    ])
#]


def test(input_type):
    input_list = _input_type_options[input_type]
    for event in event_iterator(input_list, 'Nominal', _branch_list, 100):
        #tp = list(event['truth_particles'])
        tp = [ x.copy() for x in event['truth_particles'] ]
        rj = list(event['reco_jets'])
        print(tp)
        print()
        print(rj)
        print('\n------------\n')
        

test('sig')
