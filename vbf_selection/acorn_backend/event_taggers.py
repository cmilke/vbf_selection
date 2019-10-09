from uproot_methods import TLorentzVector

# Don't use the base tagger. Ever.
class base_tagger():
    key = 'NOOOOOO'

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

    def __init__(self, event, selections):
        jet_list = event.jets
        delta_eta = abs( jet_list[selections[0]].eta - jet_list[selections[1]].eta )
        self.discriminant = delta_eta


class unified_delta_eta_tagger(base_tagger):
    key = 'united-Deta'

    def __init__(self, event, selections):
        jet_list = event.jets
        if len(selections) == 2: self.discriminant =  delta_eta_tagger(jet_list, selections)

        simple_eta = jet_list[selections[0]].eta
        j1 = jet_list[selections[1]]
        j2 = jet_list[selections[2]]
        v1 = TLorentzVector.from_ptetaphim(j0.pt, j0.eta, j0.phi, j0.m)
        v2 = TLorentzVector.from_ptetaphim(j2.pt, j2.eta, j2.phi, j2.m)
        unified_vector = v1+v2
        unified_eta = unified_vector.eta

        delta_eta = abs( simple_eta - unified_eta )
        self.discriminant = delta_eta


class mjj_tagger(base_tagger):
    key = 'mjj'

    def __init__(self, event, selections):
        jet_list = event.jets
        j0 = jet_list[selections[0]]
        j1 = jet_list[selections[1]]
        v0 = TLorentzVector.from_ptetaphim(j0.pt, j0.eta, j0.phi, j0.m)
        v1 = TLorentzVector.from_ptetaphim(j1.pt, j1.eta, j1.phi, j1.m)
        combined = v0 + v1
        mjj = combined.mass
        self.discriminant = mjj


class mjjj_tagger(base_tagger):
    key = 'mjjj'

    def __init__(self, event, selections):
        jet_list = event.jets
        total_4vector = TLorentzVector(0,0,0,0)
        for jet in jet_list:
            vec = TLorentzVector.from_ptetaphim(jet.pt, jet.eta, jet.phi, jet.m)
            total_4vector += vec
        mjjj = total_4vector.mass
        self.discriminant = mjjj


tagger_class_list = [
    delta_eta_tagger,
    #unified_delta_eta_tagger,
    mjj_tagger,
    mjjj_tagger
]
