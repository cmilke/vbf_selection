import sys
sys.path.append('/nfs/slac/g/atlas/u02/cmilke/analysis/util')
import math
import pickle
from vbf_backend.cmilke_jets import cmilke_jet
import cmilke_analysis_utils as cutils

_input_type_options = {
    'sig': cutils.Flavntuple_list_VBFH125_gamgam[:1],
    'bgd': cutils.Flavntuple_list_ggH125_gamgam[:1]
}
_reco_branches = ['j0truthid', 'j0_isTightPhoton', 'j0_isPU', 'j0pT', 'j0eta', 'j0phi', 'j0m']
_branch_list = _reco_branches


def study_jets():
    input_type = 'sig'
    input_list = _input_type_options[input_type]
    truthIDs = []
    for event in cutils.event_iterator(input_list, 'Nominal', _branch_list, 10000, 0):
        num_quark_jets = 0
        num_jets = 0
        alt_id = -19
        for rj in cutils.jet_iterator(_reco_branches, event):
            if not cutils.passes_std_jet_cuts(rj['j0pT'], rj['j0eta']): continue
            if rj['j0_isTightPhoton']: continue
            if rj['j0truthid'] in cutils.PDG['quarks']: num_quark_jets += 1
            else: alt_id = rj['j0truthid'] 
            num_jets += 1

        if num_jets == 3 and num_quark_jets == 2: truthIDs.append(alt_id)
    print(truthIDs)

study_jets()
