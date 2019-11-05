#!/usr/bin/env python

import sys
sys.path.append('/nfs/slac/g/atlas/u02/cmilke/analysis/util')
import cmilke_analysis_utils as cutils
import math
import pickle

#Define all the high level root stuff: ntuple files, branches to be used
_input_type_options = {
    'sig': cutils.Flavntuple_list_VBFH125_gamgam[:1],
    'bgd': cutils.Flavntuple_list_ggH125_gamgam[:1]
}
_tpart_branches = [ 'tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi' ]
_tjet_branches = [ 'truthjpT', 'truthjeta', 'truthjphi', 'truthjm' ]
_reco_branches = ['j0truthid', 'j0_isTightPhoton', 'j0_isPU', 
                    'j0_JVT', 'j0_fJVT_Tight',
                    'j0pT', 'j0eta', 'j0phi', 'j0m']

_branch_list = _tpart_branches+_tjet_branches+_reco_branches
_truthj_branch_index = len(_tpart_branches)
_reco_branch_index = _truthj_branch_index + len(_tjet_branches)

def jet_matches(eta1, phi1, eta2, phi2):
    delta_eta = abs(eta1 - eta2)
    delta_phi = abs(phi1 - phi2)
    delta_R = math.hypot(delta_eta, delta_phi)
    return ( delta_R < 0.3 )


def record_reco_jets(is_sig, truth_particles, truth_jets, reco_jets):
    recorded_ids = []

    # Loop over reco jets
    num_quark_jets = 0
    for rj in cutils.jet_iterator(_reco_branches, reco_jets):
        if not cutils.passes_std_jet_cuts(rj['j0pT'], rj['j0eta']) or rj['j0_isTightPhoton']: continue

        matched = False
        #for tp in cutils.jet_iterator(_tpart_branches, truth_particles):
        for tj in cutils.jet_iterator(_tjet_branches, truth_jets):
            if jet_matches(rj['j0eta'], rj['j0phi'], tj['truthjeta'], tj['truthjphi']):
                matched = True
                break
        if rj['j0truthid'] in cutils.PDG['quarks']: num_quark_jets += 1
        recorded_ids.append( (rj['j0truthid'], matched, rj['j0_isPU']) )

    if num_quark_jets == 2 and len(recorded_ids) == 3:
        for rid, matched, pu in recorded_ids:
            print('{:-3d} {} {}'.format(rid, matched, pu))
        print()




def record_events(input_type):
    # Iterate over each event in the ntuple list,
    input_list = _input_type_options[input_type]
    is_sig = input_type == 'sig'
    for event in cutils.event_iterator(input_list, 'Nominal', _branch_list, 1000, 0):
        truth_particles = event[:_truthj_branch_index]
        truth_jets = event[_truthj_branch_index:_reco_branch_index]
        reco_jets = event[_reco_branch_index:]
        record_reco_jets(is_sig, truth_particles, truth_jets, reco_jets)

    #pickle.dump( event_data_dump, open('output.p', 'wb') )


record_events('sig')
