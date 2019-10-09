from acorn_backend import acorn_utils as autils
from acorn_backend.jet_selectors import selector_options

class acorn_jet:
    def __init__(self, pt, eta, phi, m, pdgid, pu, JVT, fJVT):
        self.pt = pt
        self.eta = eta
        self.phi = phi
        self.m = m
        self.truth_id = pdgid
        self.is_pileup = pu
        self.marked_pileup = (JVT or fJVT)

    @classmethod
    def from_reco(cls, rj):
        return acorn_jet( 
            rj['j0pT'], rj['j0eta'], rj['j0phi'],
            rj['j0m'], rj['j0truthid'], rj['j0_isPU'],
            rj['j0_JVT'], rj['j0_fJVT_Tight']
        )

    def __repr__(self):
        representation = '|---|---|---'
        representation += '(pt:{: 4.0f}, eta:{: 1.2f}, phi:{: 2.2f}, m:{: 2.1f}, id:{})'.format(
            self.pt, self.eta, self.phi, self.m, self.truth_id,
        )
        return representation

    def is_truth_quark(self):
        return self.truth_id in autils.PDG['quarks']
        

class acorn_event:
    def __init__(self, jet_list, is_bgd):
        self.jets = jet_list
        self.is_background = is_bgd
        self.selectors = []

        selector_class_list = selector_options[ len(jet_list) ]
        for selector_class in selector_class_list:
            new_selector = selector_class(self)
            self.selectors.append(new_selector)

    def __repr__(self):
        rep = '|---|---Signal Jets:\n'
        for jet in self.jets: rep += str(jet)+'\n'
        rep += '|---|\n|---|---Selectors:\n'
        for selector in self.selectors: rep += str(selector) + '\n'
        return rep
