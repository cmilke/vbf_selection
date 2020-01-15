from uproot_methods import TLorentzVector
from acorn_backend import analysis_utils as autils
from acorn_backend.acorn_containers import acorn_jet


def match_aviv_reco_jet(vector_to_match, truth_particles):
    #maxPt = -1
    #maxPtPDGID = -1
    for tp in truth_particles:
        if tp['tpartpdgID'] == autils.PDGID['photon']:
            if tp['tpartstatus'] != autils.Status['photon_out']: continue
        elif tp['tpartstatus'] != autils.Status['outgoing']: continue

        truth_vec = TLorentzVector.from_ptetaphim(tp['tpartpT'], tp['tparteta'], tp['tpartphi'], tp['tpartm'])
        deltaR = vector_to_match.delta_r(truth_vec)
        if deltaR < 0.3: return tp['tpartpdgID']
    return -1


def record_aviv_reco_jets(is_signal, event, event_data_dump):
    # Loop over reco jets and convert them into generic acorn_jet objects
    truth_particles = [ tp.copy() for tp in event['truth_particles'] ]
    recorded_jets = []
    for rj in event['reco_jets']:
        v = TLorentzVector.from_ptetaphim(rj['j0pT'], rj['j0eta'], rj['j0phi'], rj['j0m'])
        pdgid = match_aviv_reco_jet(v, truth_particles)
        is_pileup = rj['j0_isPU']
        new_jet = acorn_jet(v, pdgid, is_pileup, rj['j0_JVT'], rj['j0_fJVT_Tight'], rj['j0_QGTagger'])
        recorded_jets.append(new_jet)

    # Categorize event, and then either discard the event or perform tagging on it
    for category in event_data_dump.values():
        category.add_event(recorded_jets, is_signal, event['eventWeight'])


def record_aviv_truth_jets(is_signal, event, event_data_dump):
    # Loop over truth jets and convert them into generic acorn_jet objects
    truth_particles = list(event['truth_particles'])
    recorded_jets = []
    for tj in event['truth_jets']:
        v = TLorentzVector.from_ptetaphim(tj['truthjpT'], tj['truthjeta'], tj['truthjphi'], tj['truthjm'])
        pdgid = match_aviv_reco_jet(v, truth_particles)

        # Create jet object storing the essential aspects of the ntuple truth jet,
        # faking some of the data normally associated with reco jets
        new_jet = acorn_jet(v, pdgid, False, True, True, -1)
        recorded_jets.append(new_jet)

    # Categorize event, and then either discard the event or perform tagging on it
    for category in event_data_dump.values():
        category.add_event(recorded_jets, is_signal, event['eventWeight'])


def record_aviv_truth_particles(is_signal, event, event_data_dump):
    # Loop over truth particles and convert them into generic acorn_jet objects
    recorded_jets = []
    for tpart in event['truth_particles']:
        if tpart['tpartstatus'] != 23: continue
        v = TLorentzVector.from_ptetaphim(tpart['tpartpT'], tpart['tparteta'], tpart['tpartphi'], tpart['tpartm'])
        pdgid = tpart['tpartpdgID']

        # Create jet object storing the essential aspects of the ntuple truth particle,
        # faking some of the data normally associated with reco jets
        new_jet = acorn_jet(v, pdgid, False, True, True, -1)
        recorded_jets.append(new_jet)

    # Categorize event, and then either discard the event or perform tagging on it
    for category in event_data_dump.values():
        category.add_event(recorded_jets, is_signal, event['eventWeight'])
