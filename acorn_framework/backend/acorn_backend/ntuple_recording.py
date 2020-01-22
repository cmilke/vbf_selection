from uproot_methods import TLorentzVector
from acorn_backend.uproot_wrapper import event_iterator
from acorn_backend import analysis_utils as autils
from acorn_backend.acorn_containers import acorn_jet


def match_aviv_reco_jet(vector_to_match, truth_particles):
    for tp in truth_particles:
        if tp['tpartpdgID'] == autils.PDGID['photon']:
            if tp['tpartstatus'] != autils.Status['photon_out']: continue
        elif tp['tpartstatus'] != autils.Status['outgoing']: continue

        truth_vec = TLorentzVector.from_ptetaphim(tp['tpartpT'], tp['tparteta'], tp['tpartphi'], tp['tpartm'])
        deltaR = vector_to_match.delta_r(truth_vec)
        if deltaR < 0.3: return tp['tpartpdgID']
    return -1


def record_aviv_reco_jets(is_signal, input_list, events_to_read, event_data_dump):
    tree_name = 'Nominal'
    branches = [
        'eventWeight',
        ('truth_particles',
            ['tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm']
        ),
        ('reco_jets',
            ['j0_isPU', 'j0_QGTagger', 'j0_JVT', 'j0_fJVT_Tight', 'j0pT', 'j0eta', 'j0phi', 'j0m']
        )
    ]

    for event in event_iterator(input_list, tree_name, branches, events_to_read):
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


def record_cmilkeV1_truth_jets(is_signal, input_list, events_to_read, event_data_dump):
    tree_name = 'ntuple'
    branches = [
        'EventWeight',
        ('truth_jets',
            ['TruthJetPt', 'TruthJetEta', 'TruthJetPhi', 'TruthJetM', 'TruthJetID']
        )
    ]

    for event in event_iterator(input_list, tree_name, branches, events_to_read):
        # Loop over truth jets and convert them into generic acorn_jet objects
        recorded_jets = []
        for truth_jet in event['truth_jets']:
            v = TLorentzVector.from_ptetaphim(
                    truth_jet['TruthJetPt'],
                    truth_jet['TruthJetEta'],
                    truth_jet['TruthJetPhi'],
                    truth_jet['TruthJetM']
            )
            pdgid = truth_jet['TruthJetID']

            # Create jet object storing the essential aspects of the ntuple truth jet,
            # faking some of the data normally associated with reco jets
            new_jet = acorn_jet(v, pdgid, False, True, True, -1)
            recorded_jets.append(new_jet)

        # Categorize event, and then either discard the event or perform tagging on it
        for category in event_data_dump.values():
            category.add_event(recorded_jets, is_signal, event['EventWeight'])


def record_aviv_truth_jets(is_signal, input_list, events_to_read, event_data_dump):
    tree_name = 'Nominal'
    branches = [
        'eventWeight',
        ('truth_particles',
            ['tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm']
        ),
        ('truth_jets',
            ['truthjpT', 'truthjeta', 'truthjphi', 'truthjm']
        )
    ]

    for event in event_iterator(input_list, tree_name, branches, events_to_read):
        # Loop over truth jets and convert them into generic acorn_jet objects
        truth_particles = [ tp.copy() for tp in event['truth_particles'] ]
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


def record_aviv_truth_particles(is_signal, input_list, events_to_read, event_data_dump):
    tree_name = 'Nominal'
    branches = [
        'eventWeight',
        ('truth_particles',
            ['tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm']
        )
    ]

    for event in event_iterator(input_list, tree_name, branches, events_to_read):
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
