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
