import sys
sys.path.append('/nfs/slac/g/atlas/u02/cmilke/analysis/util')
import math
import pickle
import cmilke_analysis_utils as cutils

input_type = sys.argv[1]
input_options = {
    'sig': cutils.Flavntuple_list_VBFH125_gamgam[:1],
    'bgd': cutils.Flavntuple_list_ggH125_gamgam[:1]
}

input_list = input_options[input_type]


def jet_matches(tparteta, tpartphi, truthjeta, truthjphi):
    delta_eta = abs(tparteta - truthjeta)
    delta_phi = abs(tpartphi - truthjphi)
    delta_R = math.hypot(delta_eta, delta_phi)
    return ( delta_R < 0.3 )

event_data_dump = {2:[], 3:[], 4:[], 5:[], 6:[], 7:[]}

tpart_branches = [ 'tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi' ]
tjet_branches = [ 'truthjpT', 'truthjeta', 'truthjphi', 'truthjm' ]
branch_list = tpart_branches+tjet_branches

num_quark_list = [0,0,0,0]
for event in cutils.event_iterator(input_list, 'Nominal', branch_list, 10000, 0):
    truth_particles = event[:len(tpart_branches)]
    truth_jets = event[len(tpart_branches):]

    num_non_gam_truth_jets = 0
    num_quark_jets = 0
    recorded_truth_jets = []
    for tj in cutils.jet_iterator(tjet_branches, truth_jets):
        if tj['truthjpT'] < 30: continue #skip jets with <30 GeV pt

        for tp in cutils.jet_iterator(tpart_branches, truth_particles):
            if tp['tpartstatus'] != cutils.Status['outgoing'] or tp['tpartpdgID'] == cutils.PDG['photon']: continue
            if jet_matches(tp['tparteta'], tp['tpartphi'], tj['truthjeta'], tj['truthjphi']):
                num_non_gam_truth_jets += 1
                jet_properties = [False, tj['truthjpT'], tj['truthjeta'], tj['truthjphi'], tj['truthjm']]
                if tp['tpartpdgID'] in cutils.PDG['quarks']:
                    num_quark_jets += 1
                    jet_properties[0] = True
                recorded_truth_jets.append(jet_properties)
                break

    #We need at >=2 usuable truth jets, at least 2 of which must be from quarks
    #Our project is only for 3 or more jets, but 2 jets provides a good baseline
    #for what we should expect optimal performance to look like
    if num_non_gam_truth_jets >= 2:
        if input_type == 'sig' and num_quark_jets >= 2:
            event_data_dump[len(recorded_truth_jets)].append(recorded_truth_jets)
        elif input_type == 'bgd':
            event_data_dump[len(recorded_truth_jets)].append(recorded_truth_jets)
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
pickle.dump( event_data_dump, open('data/inputs_'+input_type+'_truth.p', 'wb') )
