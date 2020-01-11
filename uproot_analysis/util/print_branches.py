#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
from acorn_backend import analysis_utils as autils
import uproot

#ntuple_file = Flavntuple_list_VBFH125_gamgam[0]
#ntuple_file = autils.Flavntuple_list_ggH125_gamgam[0]
ntuple_file = '/nfs/slac/g/atlas/u02/cmilke/mc16-xAOD-ntuple-maker/run/submitDir/data-ANALYSIS/sample.root'
#tree = uproot.rootio.open(ntuple_file)['Nominal']
tree = uproot.rootio.open(ntuple_file)['ntuple']
for key in tree.keys(): print(key)
