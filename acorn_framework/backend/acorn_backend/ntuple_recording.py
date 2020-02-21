from uproot_methods import TLorentzVector
from acorn_backend.uproot_wrapper import event_iterator
from acorn_backend import analysis_utils as autils
from acorn_backend.acorn_containers import acorn_jet, acorn_track


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
        #truth_particles = [ tp.copy() for tp in event['truth_particles'] ]
        particle_list = []
        for truth_particle in event['truth_particles']:
            if truth_particle['tpartpdgID'] == autils.PDGID['higgs']: continue
            v = TLorentzVector.from_ptetaphim(truth_particle['tpartpT'], truth_particle['tparteta'], truth_particle['tpartphi'], truth_particle['tpartm'])
            particle_list.append( (v, truth_particle['tpartpdgID'], truth_particle['tpartstatus']) )

        recorded_jets = []
        for rj in event['reco_jets']:
            v = TLorentzVector.from_ptetaphim(rj['j0pT'], rj['j0eta'], rj['j0phi'], rj['j0m'])
            pdgid = match_jet(v, particle_list)
            #is_pileup = rj['j0_isPU']
            is_pileup = rj['tj0pT'] < 0
            new_jet = acorn_jet(v, pdgid, is_pileup, rj['j0_JVT'], rj['j0_fJVT_Tight'], rj['j0_QGTagger'], None, [])
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


def record_cmilke_truth_jets(is_signal, input_list, events_to_read, event_data_dump):
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


def record_cmilke_reco_jets(is_signal, input_list, events_to_read, event_data_dump):
    tree_name = 'ntuple'
    branches = [
        'EventWeight',
        ('reco_jets', [
            'JetPt_calib', 'JetEta_calib', 'JetPhi_calib', 'JetM_calib',
            'JetFlavor', 'JetScatterType', 'JetIsTightPhoton', 'JetJVT', 'JetfJVT_tight',
            'JetPullMagnitude', 'JetPullAngle',
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
            for reco_track in reco_jet['reco_tracks']:
                track_vector = TLorentzVector.from_ptetaphim(
                        reco_track['JetTrkPt'], reco_track['JetTrkEta'],
                        reco_track['JetTrkPhi'], reco_track['JetTrkM']
                )
                new_track = acorn_track(track_vector)
                track_list.append(new_track)

            # Create jet object storing the essential aspects of the ntuple reco jet,
            new_jet = acorn_jet(jet_vector, pdgid, is_pileup,
                    reco_jet['JetJVT'], reco_jet['JetfJVT_tight'], -1,
                    jet_pull, track_list
            )
            recorded_jets.append(new_jet)

        # Categorize event, and then either discard the event or perform tagging on it
        for category in event_data_dump.values():
            category.add_event(recorded_jets, is_signal, event['EventWeight'])


