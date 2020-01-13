from uproot_methods import TLorentzVector
from acorn_backend import analysis_utils as autils
from acorn_backend.acorn_containers import acorn_jet


def match_aviv_reco_jet(vector_to_match, truth_particles):
    for tp in truth_particles:
        if tp['tpartpdgID'] == autils.PDG['photon']:
            if tp['tpartstatus'] != autils.Status['photon_out']: continue
        elif tp['tpartstatus'] != autils.Status['outgoing']: continue

        truth_vec = TLorentzVector.from_ptetaphim(tp['tpartpT'], tp['tparteta'], tp['tpartphi'], tp['tpartm'])

        deltaR = vector_to_match.delta_r(truth_vec)
        if deltaR < 0.3: return tp['tpartpdgID']
    return -1


def record_aviv_reco_jets(is_signal, event, event_data_dump):
    event_weight = event['eventWeight']

    recorded_jets = [] # Records all useable jets

    # Loop over reco jets, and append them to the appropriate lists
    truth_particles = [ tp.copy() for tp in event['truth_particles'] ]
    for rj in event['reco_jets']:
        # Filter out jets on basic pt/eta/photon cuts
        if not autils.passes_std_jet_cuts(rj['j0pT'], rj['j0eta']): continue
        v = TLorentzVector.from_ptetaphim(rj['j0pT'], rj['j0eta'], rj['j0phi'], rj['j0m'])
        pdgid = match_aviv_reco_jet(v, truth_particles)
        if pdgid == autils.PDG['photon']: continue
        #if rj['j0_isTightPhoton']: continue
        #is_pileup = rj['j0_isPU']
        is_pileup = rj['tj0pT'] < 0

        # Create jet object storing the essential aspects of the ntuple reco jet
        new_jet = acorn_jet(v, pdgid, is_pileup, rj['j0_JVT'], rj['j0_fJVT_Tight'], rj['j0_QGTagger'])
        recorded_jets.append(new_jet)

    # Categorize event, and then either discard the event or perform tagging on it
    for category in event_data_dump.values():
        category.add_event(recorded_jets, is_signal, event_weight)


def record_aviv_truth_jets(is_signal, event, event_data_dump):
    event_weight = event['eventWeight']

    recorded_jets = [] # Records all useable jets

    truth_particles = list(event['truth_particles'])
    # Loop over truth jets, and append them to the appropriate lists
    for tj in event['truth_jets']:
        # Filter out jets on basic pt/eta/photon cuts
        if not autils.passes_std_jet_cuts(tj['truthjpT'], tj['truthjeta']): continue
        v = TLorentzVector.from_ptetaphim(tj['truthjpT'], tj['truthjeta'], tj['truthjphi'], tj['truthjm'])
        pdgid = match_aviv_reco_jet(v, truth_particles)
        if pdgid == autils.PDG['photon']: continue

        # Create jet object storing the essential aspects of the ntuple reco jet
        new_jet = acorn_jet(v, pdgid, False, True, True, -1)
        recorded_jets.append(new_jet)

    # Categorize event, and then either discard the event or perform tagging on it
    for category in event_data_dump.values():
        category.add_event(recorded_jets, is_signal, event_weight)


def record_aviv_truth_particles(is_signal, event, event_data_dump):
    event_weight = event['event']['eventWeight']

    recorded_jets = [] # Records all useable jets

    # Loop over reco jets, and append them to the appropriate lists
    for tpart in event['truth_particles']:
        # Filter out jets on basic pt/eta/photon cuts
        if tpart['tpartstatus'] != 23: continue
        if not autils.passes_std_jet_cuts(tpart['tpartpT'], tpart['tparteta']): continue
        v = TLorentzVector.from_ptetaphim(tpart['tpartpT'], tpart['tparteta'], tpart['tpartphi'], tpart['tpartm'])
        pdgid = tpart['tpartpdgID']
        if pdgid == autils.PDG['photon']: continue

        # Create jet object storing the essential aspects of the ntuple reco jet,
        # faking some of the data normally associated with reco jets
        new_jet = acorn_jet(v, pdgid, False, True, True, -1)
        recorded_jets.append(new_jet)

    # Categorize event, and then either discard the event or perform tagging on it
    for category in event_data_dump.values():
        category.add_event(recorded_jets, is_signal, event_weight)


jet_recorder_options = {
    'aviv': [
        record_aviv_reco_jets,
        record_aviv_truth_jets
    ],
    'cmilkeV1': [
        None
    ],
    'data': [
        None
    ]
}
