from uproot_methods import TLorentzVector

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


class coLinearity_tagger(base_tagger):
    key = 'coLinearity'
    value_range = (0, 0.5)

    def __init__(self, event, selections):
        eta_list = [ jet.vector.eta for jet in event.jets ]
        eta_list.sort()

        eta_normalization = eta_list[2] - eta_list[0]
        extra_jet_distance_to_leftMost_jet = eta_list[1] - eta_list[0]
        colinearity_measure = extra_jet_distance_to_leftMost_jet / eta_normalization
        colinearity_discriminant = abs( colinearity_measure - 0.5 )
        self.discriminant = colinearity_discriminant
