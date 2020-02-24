from uproot_methods import TLorentzVector
import math

# Don't use the base tagger. Ever.
class base_tagger():
    key = 'NOOOOOO'
    value_range = (-1, -1)

    def __init__(self, event, selections):
        self.discriminant = 5 # Because I like five

    def __repr__(self):
        rep  = '|---|---|---|---'
        rep += 'Disc. from '
        rep += self.__class__.__name__ + ': '
        rep += str(self.discriminant)
        return rep


class delta_eta_tagger(base_tagger):
    key = 'Deta'
    value_range = (0, 10)

    def __init__(self, event, selections):
        jet_list = event.jets
        delta_eta = abs( jet_list[selections[0]].vector.eta - jet_list[selections[1]].vector.eta )
        self.discriminant = delta_eta


class unified_delta_eta_tagger(base_tagger):
    key = 'united-Deta'
    value_range = (0, 10)

    def __init__(self, event, selections):
        jet_list = event.jets
        delta_eta = 0.0
        if len(selections) == 2:
            delta_eta = abs( jet_list[selections[0]].vector.eta - jet_list[selections[1]].vector.eta )
        else:
            simple_eta = jet_list[ selections[0] ].vector.eta
            j1 = jet_list[selections[1]]
            j2 = jet_list[selections[2]]
            unified_vector = j1.vector+j2.vector
            unified_eta = unified_vector.eta
            delta_eta = abs( simple_eta - unified_eta )
        self.discriminant = delta_eta


class mjj_tagger(base_tagger):
    key = 'mjj'
    value_range = (0, 3000)

    def __init__(self, event, selections):
        jet_list = event.jets
        jet0 = jet_list[selections[0]]
        jet1 = jet_list[selections[1]]
        mjj = (jet0.vector+jet1.vector).mass
        self.discriminant = mjj


class mjjj_tagger(base_tagger):
    key = 'mjjj'
    value_range = mjj_tagger.value_range

    def __init__(self, event, selections):
        jet_list = event.jets
        total_4vector = TLorentzVector(0,0,0,0)
        for jet in jet_list: total_4vector += jet.vector
        mjjj = total_4vector.mass
        self.discriminant = mjjj


# REQUIRES at least 3 jets!
class centrality_tagger(base_tagger):
    key = 'centrality'
    value_range = (0,100)

    def __init__(self, event, selections):
        primary_jets = [ event.jets[selections[0]], event.jets[selections[1]] ]
        primary_jets.sort(key=lambda j: j.vector.eta)
        extra_index = ({0,1,2} - set(selections[:2])).pop()
        extra_jet = event.jets[extra_index]

        primary_Deta = primary_jets[1].vector.eta - primary_jets[0].vector.eta
        extra_Deta = extra_jet.vector.eta - primary_jets[0].vector.eta
        centrality = abs(2*extra_Deta / primary_Deta - 1)
        #if centrality > 1: centrality = 1.0 / centrality
        self.discriminant = centrality


# Same as above, but only using the most forward jets
# This simplifies the discriminant
class forward_centrality_tagger(base_tagger):
    key = 'Fcentrality'
    value_range = (0,1)

    def __init__(self, event, selections):
        eta_sorted_jets = sorted(event.jets, key=lambda j: j.vector.eta)
        primary_Deta = eta_sorted_jets[2].vector.eta - eta_sorted_jets[0].vector.eta
        extra_Deta = eta_sorted_jets[1].vector.eta - eta_sorted_jets[0].vector.eta
        centrality = abs(2*extra_Deta / primary_Deta - 1)
        self.discriminant = centrality
