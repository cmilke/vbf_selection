#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
from itertools import combinations

from acorn_backend import analysis_utils as autils
from acorn_backend.uproot_wrapper import event_iterator, unnest_list
from uproot_methods import TLorentzVector


_Nevents = 10000

_input_type_options = {
    'aviv': {
        'sig': autils.Flavntuple_list_VBFH125_gamgam[:1],
        'bgd': autils.Flavntuple_list_ggH125_gamgam[:1]
    }

  , 'cmilkeV1': {
        'sig': ['/nfs/slac/g/atlas/u02/cmilke/mc16-xAOD-ntuple-maker/run/signal/data-ANALYSIS/sample.root'],
        'bgd': ['/nfs/slac/g/atlas/u02/cmilke/mc16-xAOD-ntuple-maker/run/background/data-ANALYSIS/sample.root']
    }
}


_tree_options = {
    'aviv': 'Nominal'
  , 'cmilkeV1': 'ntuple'
}


_branch_options = {
    'aviv': [
        'eventWeight'
      , ('truth_particles', ['tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm'])
      #, ('truth_jets', ['truthjpT', 'truthjeta', 'truthjphi', 'truthjm'])
      , ('reco_jets',  ['j0truthid',  'j0pT', 'j0eta', 'j0phi', 'j0m', 'j0_JVT', 'j0_fJVT_Loose', 'j0_fJVT_Tight'])
    ]

  , 'cmilkeV1': [
        'EventWeight'
      , ('truth_jets', [ 'TruthJetPt', 'TruthJetEta', 'TruthJetPhi', 'TruthJetM'] )
      #, ('reco_jets', [ 'JetFlavor', 'JetPt_calib', 'JetEta_calib', 'JetPhi_calib', 'JetM_calib'] )
    ]
}


def match_jet(vector_to_match, truth_particles):
    max_pt = 0
    max_pt_pdgid = -1
    match_index = -1
    dual_matched = False
    for index, (truth_vec, pdgid, status) in enumerate(truth_particles):
        deltaR = vector_to_match.delta_r(truth_vec)
        if deltaR < 0.3 and truth_vec.pt > max_pt:
            #if max_pt_pdgid in autils.PDGID['quarks'] and pdgid not in autils.PDGID['quarks']: continue
            #if max_pt_pdgid == autils.PDGID['photon'] and pdgid not in autils.PDGID['quarks']: continue
            if max_pt_pdgid != -1: dual_matched = True
            max_pt = truth_vec.pt
            max_pt_pdgid = pdgid
            match_index = index
    if match_index != -1: truth_particles.pop(match_index)
    return max_pt_pdgid, dual_matched


def passes_cuts(input_type, jet_list):
    if len(jet_list) != 3: return False
    if jet_list[0][0].pt < 50: return False
    if input_type == 'sig':
        num_quarks = 0
        for v, is_quark in jet_list:
            if is_quark: num_quarks += 1
        if num_quarks != 2: return False
    return True


def check_if_signature_jets(jets, leading_quark_jet):
    both_jets_correct = True
    contains_leading_quark = leading_quark_jet in jets

    for jet in jets:
        if not jet[1]: both_jets_correct = False
    return both_jets_correct, contains_leading_quark


def draw(input_type):
    correct_pt = 0
    correct_mjj = 0
    contains_leading_quark_pt = 0
    contains_leading_quark_mjj = 0
    tagged_pt = 0
    tagged_mjj = 0
    events_with_3_jets = 0

    ntuple_type = 'aviv' #sys.argv[1]
    branch_list = _branch_options[ntuple_type]
    tree_name = _tree_options[ntuple_type]
    input_list = _input_type_options[ntuple_type][input_type]

    for event in event_iterator(input_list, tree_name, branch_list, _Nevents):
        particle_list = []
        for truth_particle in event['truth_particles']:
            if truth_particle['tpartpdgID'] == autils.PDGID['higgs']: continue
            v = TLorentzVector.from_ptetaphim(truth_particle['tpartpT'], truth_particle['tparteta'], truth_particle['tpartphi'], truth_particle['tpartm'])
            particle_list.append( (v, truth_particle['tpartpdgID'], truth_particle['tpartstatus']) )
            #if truth_particle['tpartpdgID'] == 22 and truth_particle['tpartstatus'] not in (1,23): print(truth_particle['tpartstatus'])

        jet_list = []
        #for jet in event['truth_jets']:
        num_dual_matched = 0
        for jet in event['reco_jets']:
            if not (jet['j0_JVT'] and jet['j0_fJVT_Tight']): continue
            #v = TLorentzVector.from_ptetaphim(jet['truthjpT'], jet['truthjeta'], jet['truthjphi'], jet['truthjm'])
            v = TLorentzVector.from_ptetaphim(jet['j0pT'], jet['j0eta'], jet['j0phi'], jet['j0m'])
            if v.pt < 30 or abs(v.eta) > 4: continue
            pdgid, dual_matched = match_jet(v, particle_list)
            if pdgid == autils.PDGID['photon']: continue
            jet_list.append( (v, pdgid in autils.PDGID['quarks']) )
        if not passes_cuts(input_type, jet_list): continue
        quark_jets = [ jet for jet in jet_list if jet[1] ]
        #print(jet_list)
        events_with_3_jets += 1


        # Leading Pt
        pt_chosen_jets = jet_list[:2]
        if input_type == 'sig':
            correct_jets, has_leading_pt = check_if_signature_jets(pt_chosen_jets, quark_jets[0])
            correct_pt += int(correct_jets)
            contains_leading_quark_pt += int(has_leading_pt)

        tagged_pt += int( (pt_chosen_jets[0][0] + pt_chosen_jets[1][0]).mass > 252 )
        
        
        # Maximized Mjj
        mass_pairs = sorted( [ ( (i[0]+j[0]).mass, [i,j] ) for i,j in combinations(jet_list, 2) ], reverse=True, key=lambda t: t[0])
        mjj_chosen_jets = mass_pairs[0][1]
        if input_type == 'sig':
            correct_jets, has_leading_pt = check_if_signature_jets(mjj_chosen_jets, quark_jets[0])
            correct_mjj += int(correct_jets)
            contains_leading_quark_mjj += int(has_leading_pt)

        tagged_mjj += int( (mjj_chosen_jets[0][0] + mjj_chosen_jets[1][0]).mass > 310 )

    num_jets = events_with_3_jets
    print()
    print(num_jets)
    if input_type == 'sig': print('{}, {}, {:.02}, {:.02} | {:.02}, {:.02}'.format(correct_pt, correct_mjj, correct_pt/num_jets, correct_mjj/num_jets, contains_leading_quark_pt/num_jets, contains_leading_quark_mjj/num_jets) )
    print('{}, {}, {:.02}, {:.02}'.format(tagged_pt, tagged_mjj, tagged_pt/num_jets, tagged_mjj/num_jets) )

        

draw('sig')
print()
draw('bgd')
