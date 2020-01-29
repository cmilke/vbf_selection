import pickle
import sys

Flavntuple_list_VBFH125_gamgam = [
        "/nfs/slac/g/atlas/u02/cmilke/datasets/VBFH125_gamgam/data-CxAOD-0.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/VBFH125_gamgam/data-CxAOD-1.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/VBFH125_gamgam/data-CxAOD-2.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/VBFH125_gamgam/data-CxAOD-3.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/VBFH125_gamgam/data-CxAOD-4.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/VBFH125_gamgam/data-CxAOD-5.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/VBFH125_gamgam/data-CxAOD-6.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/VBFH125_gamgam/data-CxAOD-7.root"
]

Flavntuple_list_ggH125_gamgam = [
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-0.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-1.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-2.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-3.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-4.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-5.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-6.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-7.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-8.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-9.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-10.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-11.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-12.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-13.root"
]

Flavntuple_list_VBFH125_gamgam_V2 = [
    '/nfs/slac/g/atlas/u02/cmilke/mc16-xAOD-ntuple-maker/run/signal/data-ANALYSIS/sample.root'
]

Flavntuple_list_ggH125_gamgam_V2 = [
    '/nfs/slac/g/atlas/u02/cmilke/mc16-xAOD-ntuple-maker/run/background/data-ANALYSIS/sample.root'
]

PDGID = {
    'down' : 1,
    'up' : 2,
    'strange' : 3,
    'charm' : 4,
    'bottom' : 5,
    'top' : 6,
    'quarks': range(1,7),
    'gluon': 21,
    'photon': 22,
    'higgs': 25
}

Status = {
    'outgoing': 23,
    'photon_out': 1
}

Pt_min = 30 #GeV
Eta_max = 4


def is_outgoing_quark(pdg, status): return (pdg in PDG['quarks'] and status == Status['outgoing'])


def passes_std_jet_cuts(pt, eta): return ( pt > Pt_min and abs(eta) < Eta_max )


def reload_data(regen, data_extraction_function, cache_dir='studies/cache/', suffix=''):
    data_file_root = sys.argv[0].split('/')[-1].split('.')[-2]
    data_file = cache_dir+data_file_root+suffix+'.p'

    if regen:
        retrieved_data_values = data_extraction_function()
        pickle.dump( retrieved_data_values, open(data_file, 'wb') )
    else:
        retrieved_data_values = pickle.load( open(data_file, 'rb') )

    print('Retrieved Data. Plotting')
    return retrieved_data_values
