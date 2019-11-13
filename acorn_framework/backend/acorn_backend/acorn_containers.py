from acorn_backend import acorn_utils as autils
from acorn_backend.tagger_loader import selector_options
from uproot_methods import TLorentzVector

class acorn_jet:
    def __init__(self, v, pdgid, pu, JVT, fJVT):
        self.vector = v
        self.truth_id = pdgid
        self.is_pileup = pu
        self.passes_JVT = (JVT and fJVT)

    def __repr__(self):
        representation = '|---|---|---'
        representation += '(pt:{: 4.0f}, eta:{: 1.2f}, phi:{: 2.2f}, m:{: 2.1f}, id:{})'.format(
            self.vector.pt, self.vector.eta, self.vector.phi, self.vector.mass, self.truth_id
        )
        return representation

    def is_truth_quark(self):
        return (self.truth_id in autils.PDG['quarks'])
        

class acorn_event:
    def __init__(self, jet_list, event_weight, is_sig, this_event_should_be_tagged):
        self.jets = jet_list
        self.event_weight = 1 #event_weight 
        self.signal = is_sig
        if this_event_should_be_tagged:
            # Use all available jet selectors to try and identify
            # which jets are the VBF signature jets.
            # The selectors will then pass themselves and the event
            # to the tagger classes for event tagging
            self.selectors = {}
            selector_class_list = selector_options[ len(jet_list) ]
            for selector_class in selector_class_list:
                self.selectors[selector_class.key] = selector_class(self)

    def __repr__(self):
        rep = '|---|---'+str(len(self.jets))+' Jets:\n'
        for jet in self.jets: rep += str(jet)+'\n'
        rep += '|---|\n|---|---Selectors:\n'
        for selector in self.selectors.values(): rep += str(selector) + '\n'
        return rep
