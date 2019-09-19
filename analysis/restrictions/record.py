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


#NOTE: the order of these keys is CRITICALLY important
#The order determines which restrictions are applied first
#Carrots (^) indicate loop-locked values that MUST go below the specified key.
#i.e. the ^ should always point towards the specified key
_restriction_base = {
    'all': 1, # Should always be first and = 1

    '>=2 minpt truth jets': 0,
    '>=3 minpt truth jets': 0,
    '>=2 non-gam truth jets': 0, # ^ minpt truth jets
    '>=3 non-gam truth jets': 0, # ^ minpt truth jets
    '>=2 q-matched truth jets': 0, # ^ minpt truth jets
    '>=3 q-matched truth jets': 0, # ^ minpt truth jets
    'END' : 0 # Must always be last and = 0
    #'2 quarks': 0,
    #'>=2 minpt truth jets': 0,
    #'>=3 minpt truth jets': 0,
    #'>=2 reco jets': 0,
    #'not tightPhoton': 0,
    #'not pileup': 0, # ^ not tightPhoton
    #'2 pass cuts': 0, # ^ not pileup
    #'2 quark-matched': 0,
    #'3 pass cuts': 0, # ^ not pileup
    #'4 pass cuts': 0, # ^ not pileup
    #'5 pass cuts': 0, # ^ not pileup
    #'6 pass cuts': 0, # ^ not pileup

}

_num_restrictions = len(_restriction_base)
availability = []


branch_list = [
    'tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi',
    'truthjpT', 'truthjeta', 'truthjphi',
    'j0truthid', 'j0_isTightPhoton', 'j0_isPU', 'j0pT', 'j0eta'
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

            restrictions = _restriction_base.copy()

            #iterate through truth jets by themselves
            num_minpt_truth_jets = 0
            valid_truthjets = []
            for truthjpT, truthjeta, truthjphi in zip( *truth_jets ):
                if truthjpT > 20:
                    num_minpt_truth_jets += 1
                    valid_truthjets.append((truthjpT, truthjeta, truthjphi))
            
            #iterate through truth particles
            num_outgoing_quarks = 0
            num_non_gam_jets = 0
            num_matched_truth_jets = 0
            matched_valid_jet_indices = {}
            for tpartpdgID, tpartstatus, tpartpT, tparteta, tpartphi in zip( *truth_particles ):
                if cutils.is_outgoing_quark(tpartpdgID, tpartstatus): num_outgoing_quarks += 1
                if tpartstatus == cutils.Status['outgoing']:
                    if tpartpdgID in cutils.PDG['quarks']: num_outgoing_quarks += 1

                    #match truth particle to truth jet
                    for index, (truthjpT, truthjeta, truthjphi) in enumerate(valid_truthjets):
                        #if index in matched_valid_jet_indices: continue
                        if jet_matches(tparteta, tpartphi, truthjeta, truthjphi):
                            if tpartpdgID != cutils.PDG['photon']: num_non_gam_jets += 1
                            if tpartpdgID in cutils.PDG['quarks']: num_matched_truth_jets += 1
                            matched_valid_jet_indices[index] = None
                            break

            #iterate through reco jets
            num_quark_matched = 0
            num_marked_notTightPhoton = 0
            num_not_pileup = 0
            num_pass_cuts = 0
            for j0truthid, j0_isTightPhoton, j0_isPU, j0pT, j0eta in zip( *reco_jets ):
                if j0truthid in cutils.PDG['quarks']: num_quark_matched += 1
                if not j0_isTightPhoton:
                    num_marked_notTightPhoton += 1
                    if not j0_isPU:
                        num_not_pileup += 1
                        if cutils.passes_std_jet_cuts(j0pT, j0eta): num_pass_cuts += 1

            #tally up all the restrictions
            if num_minpt_truth_jets >= 2: restrictions['>=2 minpt truth jets'] = 1
            if num_minpt_truth_jets >= 3: restrictions['>=3 minpt truth jets'] = 1
            if num_non_gam_jets >= 2: restrictions['>=2 non-gam truth jets'] = 1
            if num_non_gam_jets >= 3: restrictions['>=3 non-gam truth jets'] = 1
            if num_matched_truth_jets >= 2: restrictions['>=2 q-matched truth jets'] = 1
            if num_matched_truth_jets >= 3: restrictions['>=3 q-matched truth jets'] = 1
            #if num_outgoing_quarks >= 2: restrictions['2 quarks'] = 1
            #if len(event[reco_index]) >= 2: restrictions['>=2 reco jets'] = 1
            #if num_marked_notTightPhoton >= 2: restrictions['not tightPhoton'] = 1
            #if num_not_pileup >= 2: restrictions['not pileup'] = 1
            #if num_pass_cuts >= 2: restrictions['2 pass cuts'] = 1
            #if num_quark_matched == 2: restrictions['2 quark-matched'] = 1
            #if num_pass_cuts >= 3: restrictions['3 pass cuts'] = 1
            #if num_pass_cuts >= 4: restrictions['4 pass cuts'] = 1
            #if num_pass_cuts >= 5: restrictions['5 pass cuts'] = 1
            #if num_pass_cuts >= 6: restrictions['6 pass cuts'] = 1

            #Find which restriction failed first, then append that to the final list
            restriction_bin = list( restrictions.values() ).index(0) - 1
            availability.append(restriction_bin)
        if basket_number >= 0: break

#print(availability)
pickle.dump( availability, open('availability.p', 'wb') )
