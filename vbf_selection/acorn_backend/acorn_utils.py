import uproot

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
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-7.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-8.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-9.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-10.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-11.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-12.root",
        "/nfs/slac/g/atlas/u02/cmilke/datasets/ggH125_gamgam/data-CxAOD-13.root"
]

PDG = {
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
    'outgoing': 23
}

Pt_min = 30 #GeV
Eta_max = 4


def is_outgoing_quark(pdg, status): return (pdg in PDG['quarks'] and status == Status['outgoing'])


def passes_std_jet_cuts(pt, eta): return ( pt > Pt_min and abs(eta) < Eta_max )


def event_iterator(ntuple_list, tree_name, divided_branch_list, step_size, max_bucket):
    event = {}
    event_ranges = {}
    branch_list = []
    for key,sublist in divided_branch_list.items():
        start = len(branch_list)
        branch_list += sublist
        end = len(branch_list)
        event_ranges[key] = slice(start, end)
        event[key] = None
    
    
    for ntuple_file in ntuple_list:
        print('\nnutple file: ' + ntuple_file)
        tree = uproot.rootio.open(ntuple_file)[tree_name]
        tree_iterator = tree.iterate(branches=branch_list, entrysteps=step_size) 
        for basket_number, basket in enumerate(tree_iterator):
            print('Basket: ' + str(basket_number) )
            for entry in zip(*basket.values()):
                for key in divided_branch_list:
                    event[key] = entry[ event_ranges[key] ]
                yield event
            if max_bucket != None:
                if basket_number >= max_bucket: break
     

def jet_iterator(branches, jet_list):
    package = {}
    for branch_collection in zip(*jet_list):
        for index, key in enumerate(branches):
            package[key] = branch_collection[index]
        yield package
