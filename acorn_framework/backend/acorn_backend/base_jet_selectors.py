import random
import math
from uproot_methods import TLorentzVector
from acorn_backend import simple_event_taggers
from acorn_backend.machine_learning.simple_2_jet_tagger import basic_nn_tagger


# Return the first two jets.
# Should only be used for 2 jet events
class base_selector():
    key = 'null'
    tagger_class_list = [
        simple_event_taggers.mjj_tagger
      , basic_nn_tagger
      #, simple_event_taggers.delta_eta_tagger
      #, simple_event_taggers.mjjj_tagger
    ]

    def select(self, event):
        return (0,1)


    def __init__(self, event):
        self.selections = self.select(event)
        self.taggers = {}
        self.is_correct = True
        for jet in [ event.jets[i] for i in self.selections ]:
            if not jet.is_truth_quark():
                self.is_correct = False
                break

        # Tag the event with this selection,
        # with all available taggers
        for tagger_class in self.__class__.tagger_class_list:
            self.taggers[tagger_class.key] = tagger_class(event, self.selections)

    def __repr__(self):
        rep  = '|---|---|---'
        rep += self.__class__.__name__ + ': '
        rep += str(self.selections) + '\n'
        for tagger in self.taggers.values(): rep += str(tagger) + '\n'
        rep += '|---|---|'
        return rep


# Just a copy of the base_selector with a different tagger list
class dummy_2_jet_selector(base_selector):
    key = 'dummy2jet'
    tagger_class_list = [ basic_nn_tagger ]


# Select the vbf jets at random...
# This is just to establish a lower bound on performance
class random_selector(base_selector):
    key = 'random'

    def select(self, event):
        jet_indices = list( range(0,len(event.jets)) )
        random.shuffle(jet_indices)
        chosen_jets = jet_indices[:2]
        return tuple(chosen_jets)

   
# Select two highest pt jets
class highest_pt_selector(base_selector):
    key = '2maxpt'

    def select(self, event):
        jet_idents = [-1,-1]
        max_pts = [-1,-1]
        for index, jet in enumerate(event.jets):
            if jet.vector.pt > max_pts[0]:
                max_pts[1] = max_pts[0]
                jet_idents[1] = jet_idents[0]
                max_pts[0] = jet.vector.pt
                jet_idents[0] = index
            elif jet.vector.pt > max_pts[1]:
                max_pts[1] = jet.vector.pt
                jet_idents[1] = index
        return tuple(jet_idents)


# Select the two jets with the
# largest Delta-eta between them
class maximal_Delta_eta_selector(base_selector):
    key = 'etamax'

    def select(self, event):
        jet_idents = [-1,-1]
        max_delta_eta = -1
        num_jets = len(event.jets)
        for i in range(0, num_jets):
            eta0 = event.jets[i].vector.eta
            for j in range(i+1, num_jets):
                eta1 = event.jets[j].vector.eta
                delta_eta = abs(eta0 - eta1)
                if delta_eta > max_delta_eta:
                    max_delta_eta = delta_eta
                    jet_idents = [i,j]
        return tuple(jet_idents)


# Select the two jets with the largest mjj
class maximal_mjj_selector(base_selector):
    key = 'mjjmax'

    def select(self, event):
        jet_idents = [-1,-1]
        max_mjj = -1

        num_jets = len(event.jets)
        for i in range(0, num_jets):
            for j in range(i+1, num_jets):
                jet0 = event.jets[i]
                jet1 = event.jets[j]
                mjj = (jet0.vector+jet1.vector).mass
                if mjj > max_mjj:
                    max_mjj = mjj
                    jet_idents = [i,j]

        return tuple(jet_idents)


# Select the two jets with the
# largest Delta-R between them
class maximal_Delta_R_selector(base_selector):
    key = 'Rmax'

    def select(self, event):
        jet_idents = [-1,-1]
        max_delta_R = -1
        num_jets = len(event.jets)
        for i in range(0, num_jets):
            eta0 = event.jets[i].vector.eta
            phi0 = event.jets[i].vector.phi
            for j in range(i+1, num_jets):
                eta1 = event.jets[j].vector.eta
                phi1 = event.jets[j].vector.phi
                Deta = eta1 - eta0
                Dphi = phi1 - phi0
                delta_R = math.hypot(Deta, Dphi)
                if delta_R > max_delta_R:
                    max_delta_R = delta_R
                    jet_idents = [i,j]
        return tuple(jet_idents)


# Select the two jets with the largest
# product of mjj and Deta
class maximal_mjjXDeta_selector(base_selector):
    key = 'mjjXetamax'

    def select(self, event):
        jet_idents = [-1,-1]
        max_product = -1
        num_jets = len(event.jets)
        for i in range(0, num_jets):
            for j in range(i+1, num_jets):
                j0 = event.jets[i]
                j1 = event.jets[j]
                v0 = TLorentzVector.from_ptetaphim(j0.vector.pt, j0.vector.eta, j0.vector.phi, j0.vector.mass)
                v1 = TLorentzVector.from_ptetaphim(j1.vector.pt, j1.vector.eta, j1.vector.phi, j1.vector.mass)
                combined = v0 + v1
                mjj = combined.mass
                delta_eta = abs(j0.vector.eta - j1.vector.eta)
                DetaXmjj = mjj*delta_eta
                if DetaXmjj > max_product:
                    max_product = DetaXmjj
                    jet_idents = [i,j]
        return tuple(jet_idents)


# Selects the correct vbf jets based on truth info
# Returns the first two if background
class truth_selector(base_selector):
    key = 'truth'

    def select(self, event):
        jet_idents = []
        for index, jet in enumerate(event.jets):
            if jet.is_truth_quark(): jet_idents.append(index)

        if len(jet_idents) == 2:
            return tuple(jet_idents)
        else:
            jet_indices = list( range(0,len(event.jets)) )
            random.shuffle(jet_indices)
            chosen_jets = jet_indices[:2]
            return chosen_jets
