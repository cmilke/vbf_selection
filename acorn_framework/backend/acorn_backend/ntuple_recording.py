from uproot_methods import TLorentzVector
from acorn_backend import acorn_utils as autils
from acorn_backend.acorn_containers import acorn_jet


def match_aviv_reco_jet(vector_to_match, event):
    for tp in autils.jet_iterator(event['tpart']):
        if tp['tpartpdgID'] == autils.PDG['photon']:
            if tp['tpartstatus'] != autils.Status['photon_out']: continue
        elif tp['tpartstatus'] != autils.Status['outgoing']: continue

        truth_vec = TLorentzVector.from_ptetaphim(tp['tpartpT'], tp['tparteta'], tp['tpartphi'], tp['tpartm'])

        deltaR = vector_to_match.delta_r(truth_vec)
        if deltaR < 0.3: return tp['tpartpdgID']
    return -1


def record_aviv_reco_jets(is_signal, event, event_data_dump):
    event_weight = event['event']['eventWeight']

    recorded_jets = [] # Records all useable jets

    # Loop over reco jets, and append them to the appropriate lists
    for rj in autils.jet_iterator(event['j0']):
        # Filter out jets on basic pt/eta/photon cuts
        if not autils.passes_std_jet_cuts(rj['j0pT'], rj['j0eta']): continue
        v = TLorentzVector.from_ptetaphim(rj['j0pT'], rj['j0eta'], rj['j0phi'], rj['j0m'])
        pdgid = match_aviv_reco_jet(v, event)
        if pdgid == autils.PDG['photon']: continue
        #if rj['j0_isTightPhoton']: continue

        # Create jet object storing the essential aspects of the ntuple reco jet
        new_jet = acorn_jet(v, pdgid, rj['j0_isPU'], rj['j0_JVT'], rj['j0_fJVT_Tight'], rj['j0_QGTagger'])
        recorded_jets.append(new_jet)

    # Categorize event, and then either discard the event or perform tagging on it
    for category in event_data_dump.values():
        category.add_event(recorded_jets, is_signal, event_weight)


jet_recorder_options = {
    'aviv': [
        record_aviv_reco_jets,
        None
    ],
    'cmilkeV1': [
        None
    ],
    'data': [
        None
    ]
}
