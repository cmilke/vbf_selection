import random
import math
from uproot_methods import TLorentzVector
from acorn_backend.event_taggers import tagger_class_list


# Return the first two jets.
# Should only be used for 2 jet events
class base_selector():
    key = 'null'

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
        for tagger_class in tagger_class_list:
            self.taggers[tagger_class.key] = tagger_class(event, self.selections)

    def __repr__(self):
        rep  = '|---|---|---'
        rep += self.__class__.__name__ + ': '
        rep += str(self.selections) + '\n'
        for tagger in self.taggers: rep += str(tagger) + '\n'
        rep += '|---|---|'
        return rep


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
            if jet.pt > max_pts[0]:
                max_pts[1] = max_pts[0]
                jet_idents[1] = jet_idents[0]
                max_pts[0] = jet.pt
                jet_idents[0] = index
            elif jet.pt > max_pts[1]:
                max_pts[1] = jet.pt
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
            eta0 = event.jets[i].eta
            for j in range(i+1, num_jets):
                eta1 = event.jets[j].eta
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
                j0 = event.jets[i]
                j1 = event.jets[j]
                v0 = TLorentzVector.from_ptetaphim(j0.pt, j0.eta, j0.phi, j0.m)
                v1 = TLorentzVector.from_ptetaphim(j1.pt, j1.eta, j1.phi, j1.m)
                combined = v0 + v1
                mjj = combined.mass
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
            eta0 = event.jets[i].eta
            phi0 = event.jets[i].phi
            for j in range(i+1, num_jets):
                eta1 = event.jets[j].eta
                phi1 = event.jets[j].phi
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
                v0 = TLorentzVector.from_ptetaphim(j0.pt, j0.eta, j0.phi, j0.m)
                v1 = TLorentzVector.from_ptetaphim(j1.pt, j1.eta, j1.phi, j1.m)
                combined = v0 + v1
                mjj = combined.mass
                delta_eta = abs(j0.eta - j1.eta)
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


selector_options = [
    [], #0
    [], #1
    [base_selector], #2
    [maximal_Delta_eta_selector, maximal_mjj_selector, maximal_mjjXDeta_selector, truth_selector, highest_pt_selector, random_selector] #3
]
