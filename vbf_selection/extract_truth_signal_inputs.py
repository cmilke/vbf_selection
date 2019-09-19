import sys
sys.path.append('/nfs/slac/g/atlas/u02/cmilke/analysis/util')
import cmilke_analysis_utils as cutils
import math
import uproot
import pickle

def jet_matches(tparteta, tpartphi, truthjeta, truthjphi):
    delta_eta = abs(tparteta - truthjeta)
    delta_phi = abs(tpartphi - truthjphi)
    delta_R = math.hypot(delta_eta, delta_phi)
    return ( delta_R < 0.3 )


event_data_dump = []

branch_list = [
    'tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi',
    'truthjpT', 'truthjeta', 'truthjphi', 'truthjm'
]
tjet_index = branch_list.index('truthjpT')

for ntuple_file in cutils.Flavntuple_list_VBFH125_gamgam:
    tree = uproot.rootio.open(ntuple_file)['Nominal']
    for basket_number, basket in enumerate( tree.iterate(branches=branch_list, entrysteps=100) ):
        print('Basket: ' + str(basket_number) )
        for event in zip(*basket.values()):
            truth_particles = event[:tjet_index]
            truth_jets = event[tjet_index:]

            num_non_gam_truth_jets = 0
            num_quark_jets = 0
            recorded_truth_jets = []
            for truthjpT, truthjeta, truthjphi, truthjm in zip(*truth_jets):
                if truthjpT < 30: continue #skip jets with <30 GeV pt

                for tpartpdgID, tpartstatus, tpartpT, tparteta, tpartphi in zip( *truth_particles ):
                    if tpartstatus != cutils.Status['outgoing'] or tpartpdgID == cutils.PDG['photon']: continue
                    if jet_matches(tparteta, tpartphi, truthjeta, truthjphi):
                        num_non_gam_truth_jets += 1
                        jet_properties = [False, truthjpT, truthjeta, truthjphi, truthjm]
                        if tpartpdgID in cutils.PDG['quarks']:
                            num_quark_jets += 1
                            jet_properties[0] = True
                        recorded_truth_jets.append(jet_properties)
                        break

            #We need at >=3 usuable truth jets, at least 2 of which must be from quarks
            if num_non_gam_truth_jets >= 3 and num_quark_jets >= 2: event_data_dump.append(recorded_truth_jets)
        if basket_number >= 0: break

#for event in event_data_dump: print(event)
#print( len(event_data_dump) )
pickle.dump( event_data_dump, open('signal_events.p', 'wb') )
