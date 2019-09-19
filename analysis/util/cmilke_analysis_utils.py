Flavntuple_list_VBFH125_gamgam = [
#        "/nfs/slac/g/atlas/u02/cmilke/datasets/VBFH125_gamgam/data-CxAOD-0.root",
#        "/nfs/slac/g/atlas/u02/cmilke/datasets/VBFH125_gamgam/data-CxAOD-1.root",
#        "/nfs/slac/g/atlas/u02/cmilke/datasets/VBFH125_gamgam/data-CxAOD-2.root",
#        "/nfs/slac/g/atlas/u02/cmilke/datasets/VBFH125_gamgam/data-CxAOD-3.root",
#        "/nfs/slac/g/atlas/u02/cmilke/datasets/VBFH125_gamgam/data-CxAOD-4.root",
#        "/nfs/slac/g/atlas/u02/cmilke/datasets/VBFH125_gamgam/data-CxAOD-5.root",
#        "/nfs/slac/g/atlas/u02/cmilke/datasets/VBFH125_gamgam/data-CxAOD-6.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/VBFH125_gamgam/data-CxAOD-7.root"
]

PDG = {
    'down' : 1,
    'up' : 2,
    'strange' : 3,
    'charm' : 4,
    'bottom' : 5,
    'top' : 6,
    'quarks': range(1,7),
    'photon': 22,
    'higgs': 25
}

Status = {
    'outgoing': 23
}

def is_outgoing_quark(pdg, status): return (pdg in PDG['quarks'] and status == Status['outgoing'])

Pt_min = 30 #GeV
Eta_max = 4
def passes_std_jet_cuts(pt, eta): return ( pt > Pt_min and abs(eta) < Eta_max )
