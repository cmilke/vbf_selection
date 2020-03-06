import array
from acorn_backend import analysis_utils as autils
from uproot_methods import TLorentzVector

class acorn_track:
    def __init__(self, track_vector):
        self.vector = track_vector

class acorn_jet:
    def __init__(self, pdgid, pu, JVT, fJVT, qgTagger, pt, eta, phi, m, jet_pull_mag, jet_pull_angle):
        self.ints = array.array('i', [pdgid, pu, JVT and fJVT])
        self.floats = array.array('f', [pt, eta, phi, m, jet_pull_mag, jet_pull_angle])

    def is_truth_quark(self):
        return (self.truth_id() in autils.PDGID['quarks'])
    def truth_id(self):
        return self.ints[0]
    def is_pileup(self):
        return self.ints[1]
    def passes_JVT(self):
        return self.ints[2]
    def pt(self):
        return self.floats[0]
    def eta(self):
        return self.floats[1]
    def phi(self):
        return self.floats[2]
    def m(self):
        return self.floats[3]
    def vector(self):
        return TLorentzVector.from_ptetaphim(*self.floats[:4])

    def jet_pull_mag(self):
        return self.floats[4]
    def jet_pull_angle(self):
        return self.floats[5]


class acorn_event:
    def __init__(self, jet_list, event_weight, is_sig):
        self.jets = jet_list
        self.event_weight = 1 # I don't care about event_weight right now
        self.signal = is_sig
        self.num_quark_jets = 0
        for jet in jet_list:
            if jet.is_truth_quark(): self.num_quark_jets += 1

    def tag_event(self, tagger_options):
        if len(self.jets) == 2:
            available_taggers = tagger_options['2jet']
        else:
            available_taggers = tagger_options['>=3jet']

        self.discriminants = {}
        for key, tagger in available_taggers.items():
            self.discriminants[key] = tagger(self)
