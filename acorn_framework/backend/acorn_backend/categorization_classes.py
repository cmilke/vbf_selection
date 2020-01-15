from acorn_backend.categorization_base import base_categorizer, Max_jets
from acorn_backend import analysis_utils as autils

# Common Jet Filters
Minpt20 = lambda jet: jet.vector.pt > 20 # GeV
Minpt30 = lambda jet: jet.vector.pt > 30 # GeV
Minpt40 = lambda jet: jet.vector.pt > 40 # GeV
Maxeta4 = lambda jet: abs(jet.vector.eta) < 4
Notphoton = lambda jet: jet.truth_id != autils.PDGID['photon']
NoPileup = lambda jet: not jet.is_pileup
PassesJVT = lambda jet: jet.passes_JVT

# Common Event Filters
Min2jets = lambda event: len(event.jets) >= 2
Maxjets = lambda event: len(event.jets) <= Max_jets
LeadingPt50 = lambda event: max(event.jets, key=lambda j:j.vector.pt).vector.pt > 50
ExactQuarks2 = lambda event: not event.signal or event.num_quark_jets == 2
MinQuarks2 = lambda event: not event.signal or event.num_quark_jets >= 2
# Demand at most 2 jets which are not pileup
# (signal events always have at least 2 non-pileup jets)
def DemandPU(event):
    number_of_nonPileup_jets = 0
    for jet in event.jets:
        if not jet.is_pileup: number_of_nonPileup_jets += 1
    return number_of_nonPileup_jets <= 2


class bare_minumum(base_categorizer):
    key = 'minimal'
    jet_filter_list = [ Minpt30, Maxeta4, Notphoton ] 
    event_filter_list = [ Min2jets, Maxjets, LeadingPt50, ExactQuarks2 ]


# Do not allow any truth pileup jets in event
class no_pileup(bare_minumum):
    key = 'noPU'
    bare_minumum.jet_filter_list += [ NoPileup ]


# Allow only two truth non-pileup jets. 
class with_pileup(bare_minumum):
    key = 'withPU'
    bare_minumum.event_filter_list += [ DemandPU ]


# Do not allow any jets marked by JVT or fJVT
class filter_with_JVT(bare_minumum):
    key = 'JVT'
    bare_minumum.jet_filter_list += [ PassesJVT ]


# Do not allow any jets marked by JVT or fJVT,
# with the added constraint that jet pt be > 40 GeV
class filter_with_JVT_pt40(bare_minumum):
    key = 'JVTpt40'
    bare_minumum.jet_filter_list = [ Minpt40, Maxeta4, Notphoton, PassesJVT ] 


# An attempt at replicating constraints I found
# in an ATLAS paper on VBF->H->gamgam tagging
class pt_eta_v1_with_JVT(filter_with_JVT):
    key = 'PtEtaV1JVT'

    def add_event(self, jet_list, is_sig, event_weight):
        filtered_jets = [ jet for jet in jet_list if self.passes_jet_filters(jet) ]
        new_event = acorn_event(filtered_jets, event_weight, is_sig)
        for passes_event_filter in self.event_filter_list:
            if not passes_event_filter(new_event): return False

        min_Deta_requirement = 2
        leading_jets = sorted(filtered_jets, key=lambda j: j.vector.pt, reverse=True)[:2]
        Deta = abs( leading_jets[0].vector.eta - leading_jets[1].vector.eta )
        if not (Deta > min_Deta_requirement): return False

        if self.tagging_events: new_event.tag_event()
        self.events.append(new_event)
        return True


# A combination of the filter_with_JVT and no_pileup filters
class filter_with_JVT_noPU(no_pileup):
    key = 'JVTnoPU'
    no_pileup.jet_filter_list += [ PassesJVT ]
