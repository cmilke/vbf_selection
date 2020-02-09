from acorn_backend import analysis_utils as autils
from acorn_backend.tagger_loader import selector_options
from uproot_methods import TLorentzVector

class acorn_track:
    def __init__(self, track_vector):
        self.vector = track_vector


class acorn_jet:
    def __init__(self, v, pdgid, pu, JVT, fJVT, qgTagger, jet_pull, track_list):
        self.vector = v
        self.truth_id = pdgid
        self.is_pileup = pu
        self.passes_JVT = (JVT and fJVT)
        self.quark_gluon_tagger_value = qgTagger
        self.pull = jet_pull
        self.tracks = track_list

    def __repr__(self):
        representation = '|---|---|---'
        representation += '(pt:{: 4.0f}, eta:{: 1.2f}, phi:{: 2.2f}, m:{: 2.1f}, id:{})'.format(
            self.vector.pt, self.vector.eta, self.vector.phi, self.vector.mass, self.truth_id
        )
        return representation

    def is_truth_quark(self):
        return (self.truth_id in autils.PDGID['quarks'])
        

class acorn_event:
    def __init__(self, jet_list, event_weight, is_sig):
        self.jets = jet_list
        self.event_weight = 1 # I don't care about event_weight right now
        self.signal = is_sig
        self.num_quark_jets = 0
        for jet in jet_list:
            if jet.is_truth_quark(): self.num_quark_jets += 1

    def tag_event(self):
        # Use all available jet selectors to try and identify
        # which jets are the VBF signature jets.
        # The selectors will then pass themselves and the event
        # to the tagger classes for event tagging
        self.selectors = {}
        selector_class_list = selector_options[ len(self.jets) ]
        for selector_class in selector_class_list:
            self.selectors[selector_class.key] = selector_class(self)

    def __repr__(self):
        rep = '|---|---'+str(len(self.jets))+' Jets:\n'
        for jet in self.jets: rep += str(jet)+'\n'
        rep += '|---|\n|---|---Selectors:\n'
        for selector in self.selectors.values(): rep += str(selector) + '\n'
        return rep
