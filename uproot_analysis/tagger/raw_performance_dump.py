#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
from itertools import combinations

from acorn_backend import analysis_utils as autils
from acorn_backend.uproot_wrapper import basket_generator
from uproot_methods import TLorentzVector


_Nevents = 100000

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
      , 'tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm'
      #, ('truth_jets', ['truthjpT', 'truthjeta', 'truthjphi', 'truthjm'])
      , 'j0truthid',  'j0pT', 'j0eta', 'j0phi', 'j0m', 'j0_JVT', 'j0_fJVT_Loose', 'j0_fJVT_Tight'
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
    for index, (truth_vec, pdgid, status) in enumerate(truth_particles):
        deltaR = vector_to_match.delta_r(truth_vec)
        if deltaR < 0.3 and truth_vec.pt > max_pt:
            max_pt = truth_vec.pt
            max_pt_pdgid = pdgid
            match_index = index
    if match_index != -1: truth_particles.pop(match_index)
    return max_pt_pdgid


def passes_cuts(input_type, jet_list):
    if len(jet_list) != 3: return False
    if jet_list[0][0].pt < 50: return False
    num_quarks = 0
    if input_type == 'sig':
        for v, is_quark in jet_list:
            if is_quark: num_quarks += 1
        if num_quarks != 2: return False
    return True


def check_if_signature_jets(jets):
    for jet in jets:
        if not jet[1]: return False
    return True


def draw(input_type):
    correct_pt = 0
    correct_mjj = 0
    tagged_pt = 0
    tagged_mjj = 0
    events_with_3_jets = 0

    ntuple_type = 'aviv' #sys.argv[1]
    branch_list = _branch_options[ntuple_type]
    tree_name = _tree_options[ntuple_type]
    input_list = _input_type_options[ntuple_type][input_type]


    total_events_read_in = 0
    for basket in basket_generator(input_list, tree_name, branch_list):
        for event_index in range(len(basket[b'eventWeight'])):
            total_events_read_in += 1
            if total_events_read_in > _Nevents: break

            particle_list = []
            for particle_index in range(len(basket[b'tpartpdgID'][event_index])):
                if basket[b'tpartpdgID'][event_index][particle_index] == autils.PDGID['higgs']: continue
                v = TLorentzVector.from_ptetaphim(basket[b'tpartpT'][event_index][particle_index], basket[b'tparteta'][event_index][particle_index], basket[b'tpartphi'][event_index][particle_index], basket[b'tpartm'][event_index][particle_index])
                particle_list.append( (v, basket[b'tpartpdgID'][event_index][particle_index], basket[b'tpartstatus'][event_index][particle_index]) )

            jet_list = []
            #for jet in event['truth_jets']:
            num_dual_matched = 0
            for jet_index in range(len(basket[b'j0truthid'][event_index])):
                if not (basket[b'j0_JVT'][event_index][jet_index] and basket[b'j0_fJVT_Tight'][event_index][jet_index]): continue
                #v = TLorentzVector.from_ptetaphim(basket[b'truthjpT'][event_index][jet_index], basket[b'truthjeta'][event_index][jet_index], basket[b'truthjphi'][event_index][jet_index], basket[b'truthjm'][event_index][jet_index])
                v = TLorentzVector.from_ptetaphim(basket[b'j0pT'][event_index][jet_index], basket[b'j0eta'][event_index][jet_index], basket[b'j0phi'][event_index][jet_index], basket[b'j0m'][event_index][jet_index])
                if v.pt < 30 or abs(v.eta) > 4: continue
                pdgid = match_jet(v, particle_list)
                if pdgid == autils.PDGID['photon']: continue
                jet_list.append( (v, pdgid in autils.PDGID['quarks']) )
            #pt_ordered_jets = sorted(jet_list, key=lambda j: j[0].pt, reverse=True)
            if not passes_cuts(input_type, jet_list): continue
            events_with_3_jets += 1


            # Leading Pt
            #pt_chosen_jets = pt_ordered_jets[:2]
            pt_chosen_jets = jet_list[:2]
            if input_type == 'sig':
                correct_jets = check_if_signature_jets(pt_chosen_jets)
                correct_pt += int(correct_jets)

            tagged_pt += int( (pt_chosen_jets[0][0] + pt_chosen_jets[1][0]).mass > 252 )
            
            
            # Maximized Mjj
            mass_pairs = sorted( [ ( (i[0]+j[0]).mass, [i,j] ) for i,j in combinations(jet_list, 2) ], reverse=True, key=lambda t: t[0])
            mjj_chosen_jets = mass_pairs[0][1]
            if input_type == 'sig':
                correct_jets = check_if_signature_jets(mjj_chosen_jets)
                correct_mjj += int(correct_jets)

            tagged_mjj += int( (mjj_chosen_jets[0][0] + mjj_chosen_jets[1][0]).mass > 310 )
        if total_events_read_in > _Nevents: break

    num_jets = events_with_3_jets
    print()
    print(num_jets)
    if input_type == 'sig': print('{}, {}, {:.02}, {:.02}'.format(correct_pt, correct_mjj, correct_pt/num_jets, correct_mjj/num_jets) )
    print('{}, {}, {:.02}, {:.02}'.format(tagged_pt, tagged_mjj, tagged_pt/num_jets, tagged_mjj/num_jets) )

        

draw('sig')
print()
draw('bgd')
