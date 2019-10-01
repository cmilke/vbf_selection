#!/usr/bin/env python

'''
Script which runs over a list of ntuples, filtering out events and jets.
The output is a pickled dictionary containing categorized events,
where each event is a python list of "cmilke_jet" objects,
which store basic jet information used throughout the rest of the framework
'''

import sys
sys.path.append('/nfs/slac/g/atlas/u02/cmilke/analysis/util')
import math
import pickle
from vbf_backend.cmilke_jets import cmilke_jet
import cmilke_analysis_utils as cutils

#Define all the high level root stuff: ntuple files, branches to be used
_input_type_options = {
    'sig': cutils.Flavntuple_list_VBFH125_gamgam[:1],
    'bgd': cutils.Flavntuple_list_ggH125_gamgam[:1]
}
_tpart_branches = [ 'tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi' ]
_tjet_branches = [ 'truthjpT', 'truthjeta', 'truthjphi', 'truthjm' ]
_reco_branches = ['j0truthid', 'j0_isTightPhoton', 'j0_isPU', 'j0pT', 'j0eta', 'j0phi', 'j0m']
_branch_list = _tpart_branches+_tjet_branches+_reco_branches
_truthj_branch_index = len(_tpart_branches)
_reco_branch_index = _truthj_branch_index + len(_tjet_branches)


def jet_matches(tparteta, tpartphi, truthjeta, truthjphi):
    delta_eta = abs(tparteta - truthjeta)
    delta_phi = abs(tpartphi - truthjphi)
    delta_R = math.hypot(delta_eta, delta_phi)
    return ( delta_R < 0.3 )


def record_truth_jets(is_bgd, truth_particles, truth_jets, event_data_dump):
    num_non_gam_truth_jets = 0
    num_quark_jets = 0
    recorded_truth_jets = []
    for tj in cutils.jet_iterator(_tjet_branches, truth_jets):
        if not cutils.passes_std_jet_cuts(tj['truthjpT'], tj['truthjeta']): continue

        for tp in cutils.jet_iterator(_tpart_branches, truth_particles):
            if tp['tpartstatus'] != cutils.Status['outgoing'] or tp['tpartpdgID'] == cutils.PDG['photon']: continue
            if jet_matches(tp['tparteta'], tp['tpartphi'], tj['truthjeta'], tj['truthjphi']):
                num_non_gam_truth_jets += 1
                jet = cmilke_jet(tj['truthjpT'], tj['truthjeta'], tj['truthjphi'], tj['truthjm'], False)
                if tp['tpartpdgID'] in cutils.PDG['quarks']:
                    num_quark_jets += 1
                    jet.is_truth_quark = True
                recorded_truth_jets.append(jet)
                break

    #We need at >=2 usuable truth jets, at least 2 of which must be from quarks
    #Our project is only for 3 or more jets, but 2 jets provides a good baseline
    #for what we should expect optimal performance to look like
    if num_non_gam_truth_jets >= 2:
        if not is_bgd and num_quark_jets >= 2:
            event_data_dump[str(len(recorded_truth_jets))].append(recorded_truth_jets)
        else:
            event_data_dump[str(len(recorded_truth_jets))].append(recorded_truth_jets)
    return num_quark_jets


def record_reco_jets(is_bgd, truth_particles, truth_jets, reco_jets, event_data_dump):
    # Initialize different category lists
    num_quark_jets = 0
    recorded_jets = [] # Records all useable jets
    recorded_jets_no_pu = [] # Only quark jets and non-pileup jets
    recorded_jets_with_pu = [] # Only quark and pileup jets
    recorded_jets_no_fsr = [] # Only quark and non-gluon jets
    recorded_jets_with_fsr = [] # Only quark and gluon jets

    # Loop over reco jets, and append them to the appropriate lists
    for rj in cutils.jet_iterator(_reco_branches, reco_jets):
        # Filter out jets on basic pt/eta/photon cuts
        if not cutils.passes_std_jet_cuts(rj['j0pT'], rj['j0eta']) or rj['j0_isTightPhoton']: continue

        # Get properties to be used in categorization
        is_truth_quark = False
        if rj['j0truthid'] in cutils.PDG['quarks'] and not rj['j0_isPU']:
            num_quark_jets += 1
            is_truth_quark = True
        is_gluon = rj['j0truthid'] == cutils.PDG['gluon']

        # Create jet object storing the essential aspects of the ntuple reco jet
        jet = cmilke_jet(rj['j0pT'], rj['j0eta'], rj['j0phi'], rj['j0m'], is_truth_quark)

        # Append this jet to the various lists, based on the properties of the jet
        # NOTE: each list is getting a pointer to the SAME jet. Do NOT modify this jet
        # going forward, as it will modify all the lists at once
        recorded_jets.append(jet)
        if is_bgd or not rj['j0_isPU']: recorded_jets_no_pu.append(jet)
        if is_bgd or is_truth_quark or rj['j0_isPU']: recorded_jets_with_pu.append(jet)
        if is_bgd or not is_gluon: recorded_jets_no_fsr.append(jet)
        if is_bgd or is_truth_quark or (is_gluon and not rj['j0_isPU']): recorded_jets_with_fsr.append(jet)

    # Determine how many (relevant) jets are present in event, 
    # and then append the event to the corresponding data_dump list
    key = str( len(recorded_jets) )
    nopu_key = str( len(recorded_jets_no_pu) ) + 'noPU'
    pu_key = str( len(recorded_jets_with_pu) ) + 'withPU'
    noFSR_key = str( len(recorded_jets_no_fsr) ) + 'noFSR'
    FSR_key = str( len(recorded_jets_with_fsr) ) + 'withFSR'
    if is_bgd or num_quark_jets == 2:
        if key in event_data_dump: event_data_dump[key].append(recorded_jets)
        if nopu_key in event_data_dump: event_data_dump[nopu_key].append(recorded_jets_no_pu)
        if pu_key in event_data_dump: event_data_dump[pu_key].append(recorded_jets_with_pu)
        if noFSR_key in event_data_dump: event_data_dump[noFSR_key].append(recorded_jets_no_fsr)
        if FSR_key in event_data_dump: event_data_dump[FSR_key].append(recorded_jets_with_fsr)

    return num_quark_jets #currently unused, may delete


def record_events(input_type, use_truth):
    # Define all event categories
    event_data_dump = {
        '2': []
      , '3': []
      , '3noPU': []
      , '3withPU': []
      , '3noFSR': []
      , '3withFSR': []
      , '4': []
      , '4withPU': []
    }

    # Iterate over each event in the ntuple list,
    # storing/sorting/filtering events into the data_dump as it goes
    input_list = _input_type_options[input_type]
    is_bgd = input_type == 'bgd'
    for event in cutils.event_iterator(input_list, 'Nominal', _branch_list, 10000, 0):
        truth_particles = event[:_truthj_branch_index]
        truth_jets = event[_truthj_branch_index:_reco_branch_index]
        reco_jets = event[_reco_branch_index:]
        if use_truth:
            num_quark_jets = record_truth_jets(is_bgd, truth_particles, truth_jets, event_data_dump)
        else: 
            num_quark_jets = record_reco_jets(is_bgd, truth_particles, truth_jets, reco_jets, event_data_dump)

    print('\n'+input_type)
    for key,value in event_data_dump.items(): print( '{}: {}'.format(key, len(value) ) )
    # Uncomment below for debug printing
    #print()
    #for key,value in event_data_dump.items():
    #    print(key)
    #    for event in value:
    #        for jet in event: print(jet)
    #        print()
    #    print()

    # Output the event categories for use by later scripts
    pickle.dump( event_data_dump, open('data/input_'+input_type+'.p', 'wb') )


#use_truth = sys.argv[2] == 'truth'
use_truth = False

# Either run over background and signal, or pick one
if len(sys.argv) < 2:
    record_events('sig', use_truth)
    record_events('bgd', use_truth)
else:
    record_events(_input_type_options[sys.argv[1]], use_truth)
