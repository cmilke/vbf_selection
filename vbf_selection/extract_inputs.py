import sys
sys.path.append('/nfs/slac/g/atlas/u02/cmilke/analysis/util')
import math
import pickle
from cmilke_jets import cmilke_jet
import cmilke_analysis_utils as cutils

input_type = sys.argv[1]
input_type_options = {
    'sig': cutils.Flavntuple_list_VBFH125_gamgam[:1],
    'bgd': cutils.Flavntuple_list_ggH125_gamgam[:1]
}
input_list = input_type_options[input_type]

use_truth = sys.argv[2] == 'truth'


def jet_matches(tparteta, tpartphi, truthjeta, truthjphi):
    delta_eta = abs(tparteta - truthjeta)
    delta_phi = abs(tpartphi - truthjphi)
    delta_R = math.hypot(delta_eta, delta_phi)
    return ( delta_R < 0.3 )

event_data_dump = {2:[], 3:[], 4:[], 5:[], 6:[], 7:[]}

tpart_branches = [ 'tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi' ]
tjet_branches = [ 'truthjpT', 'truthjeta', 'truthjphi', 'truthjm' ]
reco_branches = ['j0truthid', 'j0_isTightPhoton', 'j0_isPU', 'j0pT', 'j0eta', 'j0phi', 'j0m']
branch_list = tpart_branches+tjet_branches+reco_branches
truthj_branch_index = len(tpart_branches)
reco_branch_index = truthj_branch_index + len(tjet_branches)


def record_truth_jets(truth_particles, truth_jets, event_data_dump):
    num_non_gam_truth_jets = 0
    num_quark_jets = 0
    recorded_truth_jets = []
    for tj in cutils.jet_iterator(tjet_branches, truth_jets):
        if not cutils.passes_std_jet_cuts(tj['truthjpT'], tj['truthjeta']): continue

        for tp in cutils.jet_iterator(tpart_branches, truth_particles):
            if tp['tpartstatus'] != cutils.Status['outgoing'] or tp['tpartpdgID'] == cutils.PDG['photon']: continue
            if jet_matches(tp['tparteta'], tp['tpartphi'], tj['truthjeta'], tj['truthjphi']):
                num_non_gam_truth_jets += 1
                jet = cmilke_jet(False, tj['truthjpT'], tj['truthjeta'], tj['truthjphi'], tj['truthjm'])
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
            event_data_dump[len(recorded_truth_jets)].append(recorded_truth_jets)
        elif input_type == 'bgd':
            event_data_dump[len(recorded_truth_jets)].append(recorded_truth_jets)
    return num_quark_jets


def record_reco_jets(truth_particles, truth_jets, reco_jets, event_data_dump):
    num_non_gam_reco_jets = 0
    num_quark_jets = 0
    recorded_jets = []
    for rj in cutils.jet_iterator(reco_branches, reco_jets):
        if not cutils.passes_std_jet_cuts(tj['truthjpT'], tj['truthjeta']): continue
        if rj['j0_isTightPhoton'] or rj['j0_isPU']: continue
        num_non_gam_reco_jets += 1
        jet = cmilke_jet(False, rj['j0pT'], rj['j0eta'], rj['j0phi'], rj['j0m'])
        if rj['j0truthid'] in cutils.PDG['quarks']:
            num_quark_jets += 1
            jet.is_truth_quark = True
        recorded_jets.append(jet)
        break

    if num_non_gam_jets >= 2:
        if input_type == 'sig' and num_quark_jets >= 2:
            event_data_dump[len(recorded_truth_jets)].append(recorded_jets)
        elif input_type == 'bgd':
            event_data_dump[len(recorded_truth_jets)].append(recorded_jets)
    return num_quark_jets


num_quark_list = [0,0,0,0]
for event in cutils.event_iterator(input_list, 'Nominal', branch_list, 10000, 0):
    truth_particles = event[:truthj_branch_index]
    truth_jets = event[truthj_branch_index:reco_branch_index]
    reco_jets = event[reco_branch_index:]
    if use_truth:
        num_quark_jets = record_truth_jets(truth_particles, truth_jets, event_data_dump)
    else: 
        num_quark_jets = record_reco_jets(truth_particles, truth_jets, reco_jets, event_data_dump)
    num_quark_list[num_quark_jets] += 1

print('*************')
print(num_quark_list)
print('*************')
for key,value in event_data_dump.items(): print( '{}: {}'.format(key, len(value) ) )
#print()
#for key,value in event_data_dump.items():
#    print(key)
#    for event in value: print(event)
#    print()
pickle.dump( event_data_dump, open('data/input_'+input_type+'.p', 'wb') )
