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

_min_jets = 2
_max_jets = len(selector_options)-1
_leading_jet_min_pt = 50 #GeV
_demanded_number_of_quarks = 2


class base_categorizer():
    key = ''

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
    def add_event(self, jet_list, is_sig):
        filtered_jets = self.filter_jets(jet_list)
        num_jets = len(filtered_jets)

        if num_jets < _min_jets: return
        if num_jets > _max_jets: return
        if not self.passes_event_filter(filtered_jets): return

        # Iterate over jets to ensure general event requirements are still met
        # (Yes I know running over the jet list twice is inneficient,
        # But I've run speed tests and it doesn't make a difference to performance,
        # so I'm leaving it b/c it's cleaner code-wise)
        leading_jet_pt = 0.0
        num_quark_jets = 0
        for jet in jet_list:
            if jet.is_truth_quark():
                num_quark_jets += 1
            if jet.pt > leading_jet_pt:
                leading_jet_pt = jet.pt

        if leading_jet_pt < _leading_jet_min_pt: return
        if is_sig and num_quark_jets != _demanded_number_of_quarks: return

        #Create new event, which will immediately tag itself
        new_event = acorn_event(filtered_jets)
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
    key = 'noPU'

    def filter_jets(self, jet_list):
        filtered_jet_list = []
        for jet in jet_list:
            if not jet.is_pileup:
                filtered_jet_list.append(jet)
        return filtered_jet_list


# Allow only two truth non-pileup jets. 
class with_pileup(base_categorizer):
    key = 'withPU'

    def passes_event_filter(self, jet_list):
        num_not_pu = 0
        for jet in jet_list:
            if not jet.is_pileup: num_not_pu += 1
        if num_not_pu > 2: return False
        else: return True


# Do not allow any jets marked by JVT or fJVT
class filter_with_JVT(base_categorizer):
    key = 'JVT'

    def filter_jets(self, jet_list):
        filtered_jet_list = []
        for jet in jet_list:
            if jet.passes_JVT:
                filtered_jet_list.append(jet)
        return filtered_jet_list
