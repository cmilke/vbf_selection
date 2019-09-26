class cmilke_jet:
    def __init__(self, pt, eta, phi, m, is_truth_quark):
        self.pt = pt
        self.eta = eta
        self.phi = phi
        self.m = m
        self.is_truth_quark = is_truth_quark

    def __repr__(self):
        representation = '(pt:{: 4.0f}, eta:{: 1.2f}, phi:{: 2.2f}, m:{: 2.1f}, tq:{})'.format(
            self.pt,
            self.eta,
            self.phi,
            self.m,
            self.is_truth_quark,
        )
        return representation
