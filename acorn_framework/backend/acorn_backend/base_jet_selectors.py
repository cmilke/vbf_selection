import random
import math
from uproot_methods import TLorentzVector
import itertools

# Import Deep Filters
from acorn_backend import deep_filter_base

# Import simple and ML-based taggers
from acorn_backend import simple_event_taggers
from acorn_backend.machine_learning import MLtaggers

# Return the first two jets.
# Should only be used for 2 jet events
class base_selector():
    key = 'null'
    tagger_class_list = [
        simple_event_taggers.mjj_tagger
      #, simple_event_taggers.delta_eta_tagger
    ]

    deep_filter_class_list = [
        deep_filter_base.default_deep_filter
      #, deep_filter_base.mjj500_filter
    ]

    def select(self, event):
        return (0,1)


    def __init__(self, event):
        self.selections = self.select(event)
        self.is_correct = True
        for jet in [ event.jets[i] for i in self.selections[:2] ]:
            if not jet.is_truth_quark():
                self.is_correct = False
                break

        # Run the selected pair of jets through a deep filter.
        # If the pair passes the filter, add it to the filter_list
        # The filter will then apply all provided taggers to the event
        self.deep_filters = {}
        for deep_filter_class in self.__class__.deep_filter_class_list:
            if deep_filter_class.passes_filter(event, self.selections):
                filtered_selection = deep_filter_class(event, self.selections, self.__class__.tagger_class_list)
                self.deep_filters[deep_filter_class.key] = filtered_selection


    def __repr__(self):
        rep += self.__class__.__name__ + ': '
        rep += str(self.selections)
        return rep


# A base selector for 3-jet events.
# Same as the base_selector, but with added taggers
# and deep filters that only function on >3 jet events
class base_3jet_selector(base_selector):
    key = 'null3'
    tagger_class_list = base_selector.tagger_class_list + [
        simple_event_taggers.centrality_tagger
    ]

    deep_filter_class_list = base_selector.deep_filter_class_list + [
        deep_filter_base.centrality_lt06_filter
    ]


# Just a copy of the base_selector, but for taggers I don't want
# inherited by other selectors
class dummy_2_jet_selector(base_selector):
    key = 'dummy2jet'
    tagger_class_list = []


# A selector that doesn't actually do anything.
# It is intended for taggers that use all available jets,
# and do not care about selection
class dummy_3_jet_selector(base_selector):
    key = 'dummy3jet'
    tagger_class_list = [
        simple_event_taggers.mjjj_tagger 
      , simple_event_taggers.forward_centrality_tagger
      , MLtaggers.direct_3_jet_tagger
      , MLtaggers.direct_3_jet_taggerV2
      , MLtaggers.direct_3_jet_taggerV3
    ]
    deep_filter_class_list = [ deep_filter_base.default_deep_filter ]


# Select the vbf jets at random...
# This is just to establish a lower bound on performance
class random_selector(base_3jet_selector):
    key = 'random'

    def select(self, event):
        jet_indices = list( range(0,len(event.jets)) )
        random.shuffle(jet_indices)
        chosen_jets = jet_indices[:2]
        return tuple(chosen_jets)

   
# Select two highest pt jets
class highest_pt_selector(base_3jet_selector):
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
class maximal_Delta_eta_selector(base_3jet_selector):
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
class maximal_mjj_selector(base_3jet_selector):
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


# Select the two jets with the subleading mjj
# This should really only be used for experimentation...
class subleading_mjj_selector(base_3jet_selector):
    key = 'mjjSL'

    def select(self, event):
        index_combinations = itertools.combinations(range(len(event.jets)), 2)
        mass_pairs = [ ( (event.jets[i].vector+event.jets[j].vector).mass, i,j ) for i,j in index_combinations ]
        mass_pairs.sort(reverse=True, key=lambda t: t[0]) # Sort by invariant mass of the pairs, highest first
        sub_leading_mjj_pair = mass_pairs[1]
        jet_idents = sub_leading_mjj_pair[1:] # Get jet indices
        return tuple(jet_idents)


# Select the two jets with the subleading mjj
# This should REALLY only be used for experimentation...
class subsubleading_mjj_selector(base_3jet_selector):
    key = 'mjjSSL'

    def select(self, event):
        index_combinations = itertools.combinations(range(len(event.jets)), 2)
        mass_pairs = [ ( (event.jets[i].vector+event.jets[j].vector).mass, i,j ) for i,j in index_combinations ]
        mass_pairs.sort(reverse=True, key=lambda t: t[0]) # Sort by invariant mass of the pairs, highest first
        sub_sub_leading_mjj_pair = mass_pairs[2]
        jet_idents = sub_sub_leading_mjj_pair[1:] # Get jet indices
        return tuple(jet_idents)


# Select the optimal pair of jets for mjj tagging
# So, pick the highest mjj pair for signal,
# but the lowest mjj pair for background.
# WARNING: this selector is an absolute FANTASY
# It should be used for investigation ONLY.
class fantasy_optimal_mjj_selector(base_3jet_selector):
    key = 'mjjFantasy'

    def select(self, event):
        index_combinations = itertools.combinations(range(len(event.jets)), 2)
        mass_pairs = [ ( (event.jets[i].vector+event.jets[j].vector).mass, i,j ) for i,j in index_combinations ]
        mass_pairs.sort(reverse=True, key=lambda t: t[0]) # Sort by invariant mass of the pairs, highest first
        optimal_index = 0 if event.signal else -1
        optimal_mjj_pair = mass_pairs[optimal_index]
        jet_idents = optimal_mjj_pair[1:] # Get jet indices
        return tuple(jet_idents)


# Select the two jets with the
# largest Delta-R between them
class maximal_Delta_R_selector(base_3jet_selector):
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


# Selects the correct vbf jets based on truth info
# Returns mjjmax if background
class truth_selector(base_3jet_selector):
    key = 'truth'

    def select(self, event):
        jet_idents = []
        for index, jet in enumerate(event.jets):
            if jet.is_truth_quark(): jet_idents.append(index)

        if event.signal:
            return tuple(jet_idents)
        else:
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



# Picks out the quark jets based on the jets with
# the two highest quark-gluon tagger scores
class quark_gluon_tag_selector(base_3jet_selector):
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
class coLinearity_merger(base_3jet_selector):
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
