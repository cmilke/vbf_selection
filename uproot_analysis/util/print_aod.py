import uproot
import sys
sys.path.append('/nfs/slac/g/atlas/u02/cmilke/analysis/util')
import cmilke_analysis_utils as cutils

#ntuple_file = Flavntuple_list_VBFH125_gamgam[0]
ntuple_file = '/u/at/rubbo/nfs2/VBFHggyy/truthstudy/xAODdata_gamgam_VBF/mc15_13TeV.345041.PowhegPythia8EvtGen_NNPDF30_AZNLOCTEQ6L1_VBFH125_gamgam.merge.DAOD_HIGG1D1.e5720_s2726_r7772_r7676_p3015/DAOD_HIGG1D1.10692228._000001.pool.root.1'
for event in cutils.event_iterator([ntuple_file], 'CollectionTree', ['AntiKt4TruthJets'], 10, 0):
    print(event)
