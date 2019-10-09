from acorn_backend.jet_selectors import selector_options
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
and instead allow one of them to default to the base_categorizer's version.
'''


class base_categorizer():
    def __init__(self):
        self.events = []

    # Removes individual jets from the jet list
    # Includes all jets by default
    def filter_jets(self, jet_list):
        return jet_list

    # Tells category whether or not to skip this event
    # Allows all events by default
    def passes_event_filter(self, jet_list):
        return True

    # Filter jets as per the child class's rules,
    # then check if the remaining jets pass the overall event filter.
    # If so, then create a new event.
    def new_event(self, jet_list, is_bgd):
        filtered_jets = self.filter_jets(jet_list)
        num_jets = len(filtered_jets)
        min_jets = 2
        max_jets = len(selector_options)-1
        if (    min_jets <= num_jets and num_jets <= max_jets and
                self.passes_event_filter(filtered_jets) ):
            new_event = acorn_event(filtered_jets, is_bgd)
            self.events.append(new_event)

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


# Do not allow any truth pileup jets in event
class no_pileup(base_categorizer):
    def filter_jets(self, jet_list):
        filtered_jet_list = []
        for jet in jet_list:
            if not jet.is_pileup:
                filtered_jet_list.append(jet)
        return filtered_jet_list


# Allow only two truth non-pileup jets. 
class with_pileup(base_categorizer):
    def passes_event_filter(self, jet_list):
        num_not_pu = 0
        for jet in jet_list:
            if not jet.is_pileup: num_not_pu += 1
        if num_not_pu > 2: return False
        else: return True


# Do not allow any jets marked by JVT or fJVT
class filter_with_JVT(base_categorizer):
    def filter_jets(self, jet_list):
        filtered_jet_list = []
        for jet in jet_list:
            if not jet.marked_pileup:
                filtered_jet_list.append(jet)
        return filtered_jet_list
