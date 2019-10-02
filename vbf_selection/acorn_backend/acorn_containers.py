from acorn_backend import acorn_utils as autils

class acorn_jet:
    def __init__(self, pt, eta, phi, m, pdgid, pu):
        self.pt = pt
        self.eta = eta
        self.phi = phi
        self.m = m
        self.truth_id = pdgid
        self.is_pileup = pu

    @classmethod
    def from_reco(cls, rj):
        return acorn_jet( 
            rj['j0pT'],
            rj['j0eta'],
            rj['j0phi'],
            rj['j0m'],
            rj['j0truthid'],
            rj['j0_isPU']
        )

    def __repr__(self):
        representation = '(pt:{: 4.0f}, eta:{: 1.2f}, phi:{: 2.2f}, m:{: 2.1f}, id:{})'.format(
            self.pt, self.eta, self.phi, self.m, self.truth_id,
        )
        return representation

    def is_truth_quark(self):
        return self.truth_id in autils.PDG['quarks']
        

class acorn_event:
    def __init__(self, jet_list, is_bgd):
        self.jets = jet_list
        self.is_background = is_bgd

    def __repr__(self):
        representation = ''
        for jet in self.jets: representation += str(jet)+'\n'
        return representation
