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
and instead allow one of them to default to the base_categorizer's version.
'''

_min_jets = 2
_max_jets = len(selector_options)-1
_leading_jet_min_pt = 50 #GeV
_demanded_number_of_quarks = 2


# The base categorizer only filters out the bare minimum of jets
class base_categorizer():
    key = 'all'

    def __init__(self, tag_events):
        self.events = []
        self.tagging_events = tag_events

    def jet_passes_filter(self, jet):
        return True

    # Removes individual jets from the jet list
    # And records basic stats for the recorded jets
    # Includes all jets by default
    def filter_jets(self, jet_list):
        filtered_jets = []
        leading_jet_pt = 0.0
        num_quark_jets = 0
        for jet in jet_list:
            if self.jet_passes_filter(jet):
                filtered_jets.append(jet)
                if jet.is_truth_quark(): num_quark_jets += 1
                if jet.vector.pt > leading_jet_pt: leading_jet_pt = jet.vector.pt
        return (filtered_jets, leading_jet_pt, num_quark_jets)

    # Tells category whether or not to skip this event
    # Allows all events by default
    def passes_event_filter(self, jet_list):
        return True

    # Filter jets as per the child class's rules,
    # then check if the remaining jets pass the overall event filters.
    # If so, then create a new event.
    def add_event(self, jet_list, is_sig, event_weight):
        filtered_jets, leading_jet_pt, num_quark_jets = self.filter_jets(jet_list)

        # Test general event requirements
        if len(filtered_jets) < _min_jets: return
        if len(filtered_jets) > _max_jets: return
        if leading_jet_pt < _leading_jet_min_pt: return
        if is_sig and num_quark_jets != _demanded_number_of_quarks: return

        # Test category-specific event requirements
        if not self.passes_event_filter(filtered_jets): return

        #Create new event, which will immediately tag itself
        new_event = acorn_event(filtered_jets, event_weight, is_sig, self.tagging_events)
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
    def jet_passes_filter(self, jet):
        return not jet.is_pileup


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
    def jet_passes_filter(self, jet):
        return jet.passes_JVT


# Do not allow any jets marked by JVT or fJVT,
# with the added constraint that jet pt be > 40 GeV
class filter_with_JVT_pt40(base_categorizer):
    key = 'JVTpt40'
    def jet_passes_filter(self, jet):
        return jet.passes_JVT and jet.vector.pt > 40


# An attempt at replicating constraints I found
# in an ATLAS paper on VBF->H->gamgam tagging
class pt_eta_v1_with_JVT(filter_with_JVT):
    key = 'PtEtaV1JVT'
    def passes_event_filter(self, jet_list):
        min_Deta_requirement = 2
        leading_jets = sorted(jet_list, key=lambda x: x.vector.pt, reverse=True)[:2]
        Deta = abs( leading_jets[0].vector.eta - leading_jets[1].vector.eta )
        if Deta > min_Deta_requirement: return True
        else: return False


# A combination of the filter_with_JVT and no_pileup filters
class filter_with_JVT_noPU(base_categorizer):
    key = 'JVTnoPU'
    def jet_passes_filter(self, jet):
        return jet.passes_JVT and not jet.is_pileup
