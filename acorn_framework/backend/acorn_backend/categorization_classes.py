from acorn_backend.categorization_base import base_categorizer


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
