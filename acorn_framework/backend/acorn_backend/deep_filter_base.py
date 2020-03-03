class default_deep_filter():
    key = 'any'

    @classmethod
    def passes_filter(cls, event, selections):
        return True


    def __init__(self, event, selections, tagger_class_list):
        self.taggers = {}

        # Tag the event with with all provided taggers
        for tagger_class in tagger_class_list:
            self.taggers[tagger_class.key] = tagger_class(event, selections)


    def __repr__(self):
        return self.__class__.__name__


class mjj500_filter(default_deep_filter):
    key = 'mjj500'

    @classmethod
    def passes_filter(cls, event, selections):
        jet_list = event.jets
        jet0 = jet_list[selections[0]]
        jet1 = jet_list[selections[1]]
        mjj = (jet0.vector+jet1.vector).mass
        return mjj > 500 # GeV


def _get_centrality(event, selections):
    primary_jets = [ event.jets[selections[0]], event.jets[selections[1]] ]
    primary_jets.sort(key=lambda j: j.vector.eta)
    extra_index = ({0,1,2} - set(selections[:2])).pop()
    extra_jet = event.jets[extra_index]

    primary_Deta = primary_jets[1].vector.eta - primary_jets[0].vector.eta
    extra_Deta = extra_jet.vector.eta - primary_jets[0].vector.eta
    centrality = abs(2*extra_Deta / primary_Deta - 1)
    return centrality


# REQUIRES at least 3 jets!
class centrality_gt1_filter(default_deep_filter):
    key = 'central>1'

    @classmethod
    def passes_filter(cls, event, selections):
        return _get_centrality(event,selections) > 1


class centrality_lt1_filter(default_deep_filter):
    key = 'central<1'

    @classmethod
    def passes_filter(cls, event, selections):
        return _get_centrality(event,selections) < 1


class centrality_lt06_filter(default_deep_filter):
    key = 'central<0.6'

    @classmethod
    def passes_filter(cls, event, selections):
        return _get_centrality(event,selections) < 0.6


class centrality_gt06_filter(default_deep_filter):
    key = 'central>0.6'

    @classmethod
    def passes_filter(cls, event, selections):
        return _get_centrality(event,selections) > 0.6
