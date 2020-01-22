#!/usr/bin/env python
from acorn_backend import analysis_utils as autils
from acorn_backend.uproot_wrapper import event_iterator

input_list = autils.Flavntuple_list_VBFH125_gamgam

_branch_list = [
    'eventWeight',
    ('truth_particles',  ['tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm']),
    ('truth_jets', ['truthjpT', 'truthjeta', 'truthjphi', 'truthjm']),
    ('reco_jets',  ['tj0pT', 'j0truthid', 'j0_isTightPhoton', 'j0_isPU', 
                        'j0_JVT', 'j0_fJVT_Loose', 'j0_fJVT_Tight', 'j0pT', 'j0eta', 'j0phi', 'j0m'])
]

_Nevents = None


def test():
    meaningless_number = 0


    for event in event_iterator(input_list, 'Nominal', _branch_list, _Nevents):
        meaningless_number += event['eventWeight']
        for truth_jet in event['truth_particles']:
            meaningless_number += truth_jet['tpartpdgID']
            meaningless_number += truth_jet['tpartstatus']
            meaningless_number += truth_jet['tpartpT']
            meaningless_number += truth_jet['tparteta']

        for reco_jet in event['reco_jets']:
            meaningless_number += reco_jet['j0truthid']
            meaningless_number += reco_jet['j0_isTightPhoton']
            meaningless_number += reco_jet['j0pT']
            meaningless_number += reco_jet['j0eta']

    print(meaningless_number)


test()
