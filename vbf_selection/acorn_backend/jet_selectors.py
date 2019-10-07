import random
from acorn_backend.event_taggers import tagger_class_list


# Return the first two jets.
# Should only be used for 2 jet events
class base_selector():
    def select(self, event):
        return (0,1)
        
    def __init__(self, event):
        self.selections = self.select(event)

        self.taggers = []
        for tagger_class in tagger_class_list:
            new_tagger = tagger_class(event, self.selections)
            self.taggers.append(new_tagger)


# Select the vbf jets at random...
# This is just to establish a lower bound on performance
class random_selector(base_selector):
    def select(self, event):
        jet_indices = list( range(0,len(event.jets)) )
        random.shuffle(jet_indices)
        chosen_jets = jet_indices[:2]
        return tuple(chosen_jets)

   
# Select two highest pt jets
class highest_pt_selector(base_selector):
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
class maximal_eta_selector(base_selector):
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


# Selects the correct vbf jets based on truth info
# Returns the first two if background
class truth_selector(base_selector):
    def select(self, event):
        jet_idents = []
        for index, jet in enumerate(event.jets):
            if jet.is_truth_quark(): jet_idents.append(index)

        if len(jet_idents) == 2: return tuple(jet_idents)
        else: return (0,1)

selector_options = [
    [], #0
    [], #1
    [base_selector], #2
    [highest_pt_selector, maximal_eta_selector, truth_selector, random_selector] #3
]
