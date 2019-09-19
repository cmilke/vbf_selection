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
    'truthjpT', 'truthjeta', 'truthjphi',
    'j0truthid', 'j0_isTightPhoton', 'j0_isPU', 'j0pT', 'j0eta', 'j0phi', 'j0m'
]
tjet_index = branch_list.index('truthjpT')
reco_index = branch_list.index('j0truthid')

for ntuple_file in cutils.Flavntuple_list_VBFH125_gamgam:
    tree = uproot.rootio.open(ntuple_file)['Nominal']
    for basket_number, basket in enumerate( tree.iterate(branches=branch_list, entrysteps=10000) ):
        print('Basket: ' + str(basket_number) )
        for event in zip(*basket.values()):
            truth_particles = event[0:tjet_index]
            truth_jets = event[tjet_index:reco_index]
            reco_jets = event[reco_index:]

            #iterate through truth particles
            num_non_gam_truth_jets = 0
            matched_valid_jet_indices = {}
            for tpartpdgID, tpartstatus, tpartpT, tparteta, tpartphi in zip( *truth_particles ):
                if tpartstatus != cutils.Status['outgoing'] or tpartpdgID == cutils.PDG['photon']: continue

                #match truth particle to truth jet
                for index, (truthjpT, truthjeta, truthjphi) in enumerate( zip(*truth_jets) ):
                    #if index in matched_valid_jet_indices: continue
                    if truthjpT < 20: continue #skip jets with <20 GeV pt
                    if jet_matches(tparteta, tpartphi, truthjeta, truthjphi):
                        num_non_gam_truth_jets += 1
                        matched_valid_jet_indices[index] = None
                        break
            #we only care about events with >=3 non-photon jets
            if num_non_gam_truth_jets < 3: continue

            #iterate through reco jets
            num_pass_cuts = 0
            num_quark_matched = 0
            recorded_reco_jets = []
            for j0truthid, j0_isTightPhoton, j0_isPU, j0pT, j0eta, j0phi, j0m in zip( *reco_jets ):
                if j0_isTightPhoton or j0_isPU or not cutils.passes_std_jet_cuts(j0pT, j0eta): continue
                num_pass_cuts += 1
                jet_properties = [False, j0pT, j0eta, j0phi, j0m]

                if j0truthid in cutils.PDG['quarks']:
                    num_quark_matched += 1
                    jet_properties[0] = True

                recorded_reco_jets.append(jet_properties)

            #We need at >=3 usuable reco jets, at least 2 of which must be from quarks
            if num_pass_cuts < 3 or num_quark_matched < 2: continue
            event_data_dump.append(recorded_reco_jets)
        if basket_number >= 0: break

#for event in event_data_dump: print(event)
print( len(event_data_dump) )
pickle.dump( event_data_dump, open('signal_events.p', 'wb') )
