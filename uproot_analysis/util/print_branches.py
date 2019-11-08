#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
from acorn_backend import acorn_utils as autils
import uproot

#ntuple_file = Flavntuple_list_VBFH125_gamgam[0]
ntuple_file = autils.Flavntuple_list_ggH125_gamgam[0]
tree = uproot.rootio.open(ntuple_file)['Nominal']
for key in tree.keys(): print(key)
