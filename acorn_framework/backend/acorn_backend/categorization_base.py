from acorn_backend.tagger_loader import selector_options
from acorn_backend.acorn_containers import acorn_event


'''
Used to place events into different categories based on a variety of filters.
What makes this class (and its children) weird is that there are two different kinds
of filter you can impose: jet filters, and event filters.

Take for example, the "with_pileup" extension of base_categorizer, for an event with 3 jets.
This category is a strict subset of all 3-jet events; either an event has a pileup jet and
falls within this category, or does not have a pileup jet, and is excluded altogether.

In contrast to this though, notice how the "no_pileup" category works. This category strips
events of pileup jets, so looking again at 3-jet events, the no_pileup category is NOT a subset
of all 3-jet events. This is because a 3-jet event which includes a pileup jet is not excluded
from tagging, but is instead reduced to a 2-jet event which is tagged.

Because of these annoying differences in categorization methods, each category has BOTH a
jet-level filter, which strips jets out of an event; and an event-level filter, which 
excludes an event from existing at all. However, most of the categories do not implement both filters,
and instead allow one of them to default to the minimal version.
'''

Max_jets = len(selector_options)-1


# The base categorizer only filters out the bare minimum of jets
class base_categorizer():
    key = 'all'
    jet_filter_list = []
    event_filter_list = []

    def __init__(self):
        self.events = []

    def passes_jet_filters(self, jet):
        for passes_filter in self.__class__.jet_filter_list:
            if not passes_filter(jet): return False
        return True

    def add_event(self, jet_list, is_sig, event_weight):
        filtered_jets = [ jet for jet in jet_list if self.passes_jet_filters(jet) ]
        new_event = acorn_event(filtered_jets, event_weight, is_sig)
        for passes_event_filter in self.__class__.event_filter_list:
            if not passes_event_filter(new_event): return False
        self.events.append(new_event)
        return True

    def tag_events(self):
        for index, event in enumerate(self.events):
            event.tag_event()
            if index % 1000 == 0:
                print('...Tagged ' + str(index))

    def summary(self):
        summary  = 'Category ' + self.__class__.__name__ + ': '
        summary += str(len(self.events)) + ' Events'
        return summary

    def __repr__(self):
        rep = self.summary() + '\n'
        for i,event in enumerate(self.events):
            rep += '|---Event ' + str(i) + '\n'
            rep += str(event)
            rep += '|\n'
        rep += '==============\n\n'
        return rep
