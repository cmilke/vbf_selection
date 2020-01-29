import random
import math
from uproot_methods import TLorentzVector

# Import all taggers I use
from acorn_backend import simple_event_taggers
from acorn_backend.machine_learning.simple_2_jet_tagger import basic_nn_tagger
from acorn_backend.machine_learning.direct_3_jet_tagger import direct_3_jet_tagger


# Return the first two jets.
# Should only be used for 2 jet events
class base_selector():
    key = 'null'
    tagger_class_list = [
        simple_event_taggers.mjj_tagger
      #, basic_nn_tagger
      #, simple_event_taggers.delta_eta_tagger
      #, simple_event_taggers.mjjj_tagger
    ]

    def select(self, event):
        return (0,1)


    def __init__(self, event):
        self.selections = self.select(event)
        self.taggers = {}
        self.is_correct = True
        for jet in [ event.jets[i] for i in self.selections[:2] ]:
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


# Does not actually select jets.
# Meant for 2-jet taggers that do not depend on selections
class dummy_2_jet_selector(base_selector):
    key = 'dummy2jet'
    tagger_class_list = [ simple_event_taggers.mjjj_tagger ]


# As above, but for 3-jet taggers
class dummy_3_jet_selector(base_selector):
    key = 'dummy3jet'
    tagger_class_list = [ direct_3_jet_tagger ]
    #tagger_class_list = [ simple_event_taggers.coLinearity_tagger ]


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

        if len(jet_idents) >= 2:
            return tuple(jet_idents)
        else:
            jet_indices = list( range(0,len(event.jets)) )
            random.shuffle(jet_indices)
            chosen_jets = jet_indices[:2]
            return tuple(chosen_jets)


# Picks out the quark jets based on the jets with
# the two highest quark-gluon tagger scores
class quark_gluon_tag_selector(base_selector):
    key = 'qgtag'

    def select(self, event):
        quark_gluon_scores = [ (jet.quark_gluon_tagger_value, i) for i,jet in enumerate(event.jets) ]
        quark_gluon_scores.sort()
        jet_idents = [ index for (qgScore, index) in quark_gluon_scores ]
        return tuple(jet_idents[:2])




# Select the two jets with the largest mjj
# then possibly merge the third jet based on co-linearity.
# The tuple is arranged such that the 0 and 2 index jets
# are the colinear jets, with jets 0 and 1 still being the VBF jets.
class coLinearity_merger(base_selector):
    key = 'coLinear-mjj'
    tagger_class_list = [ simple_event_taggers.unified_delta_eta_tagger ]

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

        eta_list = [ (jet.vector.eta,i) for i,jet in enumerate(event.jets) ]
        eta_list.sort() # sort by eta

        eta_normalization = eta_list[2][0] - eta_list[0][0]
        extra_jet_distance_to_leftMost_jet = eta_list[1][0] - eta_list[0][0]
        colinearity_measure = (extra_jet_distance_to_leftMost_jet / eta_normalization) - 0.5

        if abs(colinearity_measure) < 0.3:
            return tuple(jet_idents)
        else:
            colinear_eta_index = 0 if colinearity_measure < 0 else 2
            colinear_jet_index = eta_list[colinear_eta_index][1]
            colinear_pair = [ eta_list[1][1], colinear_jet_index ]
            colinear_pair.sort()
            if colinear_pair == jet_idents:
                return tuple(jet_idents)
            else:
                radiated_index = eta_list[1][1] if colinear_jet_index in jet_idents else colinear_jet_index

                merged_jet_idents = [-1,-1,-1]
                if colinear_jet_index == 0:
                    merged_jet_idents = jet_idents + [ radiated_index ]
                else:
                    merged_jet_idents = jet_idents[::-1] + [ radiated_index ]
                return merged_jet_idents
