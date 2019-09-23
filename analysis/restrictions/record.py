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

    '>=2 reco jets': 0,
    'not tightPhoton': 0,
    'not pileup': 0, # ^ not tightPhoton
    '2 pass cuts': 0, # ^ not pileup
    '3 pass cuts': 0, # ^ not pileup
    '4 pass cuts': 0, # ^ not pileup
    #'>=2 minpt truth jets': 0,
    #'>=3 minpt truth jets': 0,
    #'>=2 non-gam truth jets': 0, # ^ minpt truth jets
    #'>=3 non-gam truth jets': 0, # ^ minpt truth jets
    #'>=2 q-matched truth jets': 0, # ^ minpt truth jets
    #'>=3 q-matched truth jets': 0, # ^ minpt truth jets
    'END' : 0 # Must always be last and = 0
    #'2 quarks': 0,
    #'>=2 minpt truth jets': 0,
    #'>=3 minpt truth jets': 0,
    #'2 quark-matched': 0,
    #'5 pass cuts': 0, # ^ not pileup
    #'6 pass cuts': 0, # ^ not pileup

}

_num_restrictions = len(_restriction_base)
availability = []


tpart_branches = ['tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi']
truthj_branches = ['truthjpT', 'truthjeta', 'truthjphi']
reco_branches = ['j0truthid', 'j0_isTightPhoton', 'j0_isPU', 'j0pT', 'j0eta']
branch_list = tpart_branches + truthj_branches + reco_branches
truthj_branch_index = len(tpart_branches)
reco_branch_index = truthj_branch_index + len(truthj_branches)

#files = cutils.Flavntuple_list_VBFH125_gamgam[:1]
files = cutils.Flavntuple_list_ggH125_gamgam[:1]

for event in cutils.event_iterator(files, 'Nominal', branch_list, 10000, 0):
    truth_particles = event[:truthj_branch_index]
    truth_jets = event[truthj_branch_index:reco_branch_index]
    reco_jets = event[reco_branch_index:]

    restrictions = _restriction_base.copy()

    #iterate through truth particles alone
    num_outgoing_quarks = 0
    for tp in cutils.jet_iterator(tpart_branches, truth_particles):
        if cutils.is_outgoing_quark(tp['tpartpdgID'], tp['tpartstatus']): num_outgoing_quarks += 1

    #iterate through truth jets and match to truth particles
    num_minpt_truth_jets = 0
    num_non_gam_jets = 0
    num_matched_truth_jets = 0
    for tj in cutils.jet_iterator(truthj_branches, truth_jets):
        if tj['truthjpT'] < 30: continue
        num_minpt_truth_jets += 1
        for tp in cutils.jet_iterator(tpart_branches, truth_particles):
            if tp['tpartstatus'] != cutils.Status['outgoing']: continue

            #match truth particle to truth jet
            if jet_matches(tp['tparteta'], tp['tpartphi'], tj['truthjeta'], tj['truthjphi']):
                if tp['tpartpdgID'] == cutils.PDG['photon']: continue
                if tp['tpartpdgID'] in cutils.PDG['quarks']: num_matched_truth_jets += 1
                num_non_gam_jets += 1
                break
    
    #iterate through reco jets
    num_quark_matched = 0
    num_reco_jets = 0
    num_marked_notTightPhoton = 0
    num_not_pileup = 0
    num_pass_cuts = 0
    for rj in cutils.jet_iterator(reco_branches, reco_jets):
        num_reco_jets += 1
        if rj['j0truthid'] in cutils.PDG['quarks']: num_quark_matched += 1
        if not rj['j0_isTightPhoton']:
            num_marked_notTightPhoton += 1
            if not rj['j0_isPU']:
                num_not_pileup += 1
                if cutils.passes_std_jet_cuts(rj['j0pT'], rj['j0eta']): num_pass_cuts += 1

    #tally up all the restrictions
    #if num_minpt_truth_jets >= 2: restrictions['>=2 minpt truth jets'] = 1
    #if num_minpt_truth_jets >= 3: restrictions['>=3 minpt truth jets'] = 1
    #if num_non_gam_jets >= 2: restrictions['>=2 non-gam truth jets'] = 1
    #if num_non_gam_jets >= 3: restrictions['>=3 non-gam truth jets'] = 1
    #if num_matched_truth_jets >= 2: restrictions['>=2 q-matched truth jets'] = 1
    #if num_matched_truth_jets >= 3: restrictions['>=3 q-matched truth jets'] = 1
    #if num_outgoing_quarks >= 2: restrictions['2 quarks'] = 1
    if num_reco_jets >= 2: restrictions['>=2 reco jets'] = 1
    if num_marked_notTightPhoton >= 2: restrictions['not tightPhoton'] = 1
    if num_not_pileup >= 2: restrictions['not pileup'] = 1
    if num_pass_cuts >= 2: restrictions['2 pass cuts'] = 1
    #if num_quark_matched == 2: restrictions['2 quark-matched'] = 1
    if num_pass_cuts >= 3: restrictions['3 pass cuts'] = 1
    if num_pass_cuts >= 4: restrictions['4 pass cuts'] = 1
    #if num_pass_cuts >= 5: restrictions['5 pass cuts'] = 1
    #if num_pass_cuts >= 6: restrictions['6 pass cuts'] = 1

    #Find which restriction failed first, then append that to the final list
    restriction_bin = list( restrictions.values() ).index(0) - 1
    availability.append(restriction_bin)

#print(availability)
pickle.dump( availability, open('availability_b.p', 'wb') )
