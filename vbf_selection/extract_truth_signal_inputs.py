import sys
sys.path.append('/nfs/slac/g/atlas/u02/cmilke/analysis/util')
import math
import uproot
import pickle
import cmilke_analysis_utils as cutils

def jet_matches(tparteta, tpartphi, truthjeta, truthjphi):
    delta_eta = abs(tparteta - truthjeta)
    delta_phi = abs(tpartphi - truthjphi)
    delta_R = math.hypot(delta_eta, delta_phi)
    return ( delta_R < 0.3 )


event_data_dump = []

tpart_branches = [ 'tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi' ]
tjet_branches = [ 'truthjpT', 'truthjeta', 'truthjphi', 'truthjm' ]
branch_list = tpart_branches+tjet_branches

for ntuple_file in cutils.Flavntuple_list_VBFH125_gamgam:
    tree = uproot.rootio.open(ntuple_file)['Nominal']
    for basket_number, basket in enumerate( tree.iterate(branches=branch_list, entrysteps=10000) ):
        print('Basket: ' + str(basket_number) )
        for event in zip(*basket.values()):
#for event in cutile.event_iterator(cutils.Flavntuple_list_VBFH125_gamgam, 'Nominal', branch_list, step_size):
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

            #We need at >=3 usuable truth jets, at least 2 of which must be from quarks
            if num_non_gam_truth_jets >= 3 and num_quark_jets >= 2: event_data_dump.append(recorded_truth_jets)
        if basket_number >= 0: break

#for event in event_data_dump: print(event)
print( len(event_data_dump) )
#pickle.dump( event_data_dump, open('signal_events.p', 'wb') )
