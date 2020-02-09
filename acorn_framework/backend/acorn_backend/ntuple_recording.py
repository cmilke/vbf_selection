from uproot_methods import TLorentzVector
from acorn_backend.uproot_wrapper import event_iterator
from acorn_backend import analysis_utils as autils
from acorn_backend.acorn_containers import acorn_jet, acorn_track


def match_aviv_reco_jet(vector_to_match, truth_particles):
    max_pt = 0
    max_pt_pdgid = -1
    for tp in truth_particles:
        if tp['tpartpdgID'] == autils.PDGID['higgs']: continue

        truth_vec = TLorentzVector.from_ptetaphim(tp['tpartpT'], tp['tparteta'], tp['tpartphi'], tp['tpartm'])
        deltaR = vector_to_match.delta_r(truth_vec)
        if deltaR < 0.3 and truth_vec.pt > max_pt:
            max_pt = truth_vec.pt
            max_pt_pdgid = tp['tpartpdgID']
    return max_pt_pdgid


def record_aviv_reco_jets(is_signal, input_list, events_to_read, event_data_dump):
    tree_name = 'Nominal'
    branches = [
        'eventWeight',
        ('truth_particles',
            ['tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm']
        ),
        ('reco_jets',
            ['tj0pT', 'j0_isPU', 'j0_QGTagger', 'j0_JVT', 'j0_fJVT_Tight', 'j0pT', 'j0eta', 'j0phi', 'j0m']
        )
    ]

    for event in event_iterator(input_list, tree_name, branches, events_to_read):
        # Loop over reco jets and convert them into generic acorn_jet objects
        truth_particles = [ tp.copy() for tp in event['truth_particles'] ]
        recorded_jets = []
        for rj in event['reco_jets']:
            v = TLorentzVector.from_ptetaphim(rj['j0pT'], rj['j0eta'], rj['j0phi'], rj['j0m'])
            pdgid = match_aviv_reco_jet(v, truth_particles)
            #is_pileup = rj['j0_isPU']
            is_pileup = rj['tj0pT'] < 0
            new_jet = acorn_jet(v, pdgid, is_pileup, rj['j0_JVT'], rj['j0_fJVT_Tight'], rj['j0_QGTagger'], None, [])
            recorded_jets.append(new_jet)

        # Categorize event, and then either discard the event or perform tagging on it
        for category in event_data_dump.values():
            category.add_event(recorded_jets, is_signal, event['eventWeight'])


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
            new_jet = acorn_jet(v, pdgid, False, True, True, -1, None, [])
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
            v = TLorentzVector.from_ptetaphim(
                tpart['tpartpT'], tpart['tparteta'],
                tpart['tpartphi'], tpart['tpartm']
            )
            pdgid = tpart['tpartpdgID']

            # Create jet object storing the essential aspects of the ntuple truth particle,
            # faking some of the data normally associated with reco jets
            new_jet = acorn_jet(v, pdgid, False, True, True, -1, None, [])
            recorded_jets.append(new_jet)

        # Categorize event, and then either discard the event or perform tagging on it
        for category in event_data_dump.values():
            category.add_event(recorded_jets, is_signal, event['eventWeight'])


def record_cmilkeV1_truth_jets(is_signal, input_list, events_to_read, event_data_dump):
    tree_name = 'ntuple'
    branches = [
        'EventWeight',
        ('reco_jets',
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
            if pdgid == -22: pdgid = 0
            pdgid = abs(pdgid)

            # Create jet object storing the essential aspects of the ntuple truth jet,
            # faking some of the data normally associated with reco jets
            new_jet = acorn_jet(v, pdgid, False, True, True, -1, None, [])
            recorded_jets.append(new_jet)

        # Categorize event, and then either discard the event or perform tagging on it
        for category in event_data_dump.values():
            category.add_event(recorded_jets, is_signal, event['EventWeight'])


def record_cmilkeV1_reco_jets(is_signal, input_list, events_to_read, event_data_dump):
    tree_name = 'ntuple'
    branches = [
        'EventWeight',
        ('reco_jets', [
            'JetPt_calib', 'JetEta_calib', 'JetPhi_calib', 'JetM_calib',
            'JetFlavor', 'JetScatterType', 'JetPullMagnitude', 'JetPullAngle',
            ('reco_tracks', ['JetTrkPt', 'JetTrkEta', 'JetTrkPhi', 'JetTrkM'])
        ])
    ]

    for event in event_iterator(input_list, tree_name, branches, events_to_read):
        # Loop over reco jets and convert them into generic acorn_jet objects
        recorded_jets = []
        for reco_jet in event['reco_jets']:
            jet_vector = TLorentzVector.from_ptetaphim(
                    reco_jet['JetPt_calib'], reco_jet['JetEta_calib'],
                    reco_jet['JetPhi_calib'], reco_jet['JetM_calib']
            )
            pdgid = reco_jet['JetFlavor']
            is_pileup = reco_jet['JetScatterType'] != 2
            jet_pull = (reco_jet['JetPullMagnitude'], reco_jet['JetPullAngle'])

            track_list = []
            for reco_track in reco_jet['reco_jets']:
                track_vector = TLorentzVector.from_ptetaphim(
                        reco_track['JetTrkPt'], reco_track['JetTrkEta'],
                        reco_track['JetTrkPhi'], reco_track['JetTrkM']
                )
                new_track = acorn_track(track_vector)
                track_list.append(new_track)

            # Create jet object storing the essential aspects of the ntuple reco jet,
            new_jet = acorn_jet(v, pdgid, is_pileup, not is_pileup, not is_pileup, -1, jet_pull, track_list)
            recorded_jets.append(new_jet)

        # Categorize event, and then either discard the event or perform tagging on it
        for category in event_data_dump.values():
            category.add_event(recorded_jets, is_signal, event['EventWeight'])


