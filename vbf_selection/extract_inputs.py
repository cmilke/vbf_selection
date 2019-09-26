import sys
sys.path.append('/nfs/slac/g/atlas/u02/cmilke/analysis/util')
import math
import copy
import pickle
from vbf_backend.cmilke_jets import cmilke_jet
import cmilke_analysis_utils as cutils

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


def record_truth_jets(input_type, truth_particles, truth_jets, event_data_dump):
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
        if input_type == 'sig' and num_quark_jets >= 2:
            event_data_dump[str(len(recorded_truth_jets))].append(recorded_truth_jets)
        elif input_type == 'bgd':
            event_data_dump[str(len(recorded_truth_jets))].append(recorded_truth_jets)
    return num_quark_jets


def record_reco_jets(input_type, truth_particles, truth_jets, reco_jets, event_data_dump):
    num_quark_jets = 0
    recorded_jets = []
    recorded_jets_with_pu = []
    for rj in cutils.jet_iterator(_reco_branches, reco_jets):
        if not cutils.passes_std_jet_cuts(rj['j0pT'], rj['j0eta']): continue
        if rj['j0_isTightPhoton']: continue
        jet = cmilke_jet(rj['j0pT'], rj['j0eta'], rj['j0phi'], rj['j0m'], False)
        if rj['j0truthid'] in cutils.PDG['quarks'] and not rj['j0_isPU']:
            num_quark_jets += 1
            jet.is_truth_quark = True
        recorded_jets_with_pu.append( copy.copy(jet) )
        if not rj['j0_isPU']: recorded_jets.append( copy.copy(jet) )

    key = str( len(recorded_jets) )
    pu_key = str( len(recorded_jets_with_pu) ) + 'inclPU'
    valid_for_insertion = (input_type == 'sig' and num_quark_jets >= 2) or input_type == 'bgd'
    if valid_for_insertion:
        if key in event_data_dump: event_data_dump[key].append(recorded_jets)
        if pu_key in event_data_dump: event_data_dump[pu_key].append(recorded_jets_with_pu)

    return num_quark_jets


def record_events(input_type, use_truth):
    event_data_dump = {
        '2': []
      , '3': []
      , '3inclPU': []
      , '4': []
      , '4inclPU': []
    }

    input_list = _input_type_options[input_type]
    for event in cutils.event_iterator(input_list, 'Nominal', _branch_list, 10000, 0):
        truth_particles = event[:_truthj_branch_index]
        truth_jets = event[_truthj_branch_index:_reco_branch_index]
        reco_jets = event[_reco_branch_index:]
        if use_truth:
            num_quark_jets = record_truth_jets(input_type, truth_particles, truth_jets, event_data_dump)
        else: 
            num_quark_jets = record_reco_jets(input_type, truth_particles, truth_jets, reco_jets, event_data_dump)

    for key,value in event_data_dump.items(): print( '{}: {}'.format(key, len(value) ) )
    #print()
    #for key,value in event_data_dump.items():
    #    print(key)
    #    for event in value:
    #        for jet in event: print(jet)
    #        print()
    #    print()
    pickle.dump( event_data_dump, open('data/input_'+input_type+'.p', 'wb') )


input_type = sys.argv[1]
#use_truth = sys.argv[2] == 'truth'

if input_type == 'all':
    record_events('sig', False)
    print()
    record_events('bgd', False)
else:
    record_events(_input_type_options[input_type], False)
