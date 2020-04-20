from math import pi
import os


input_dir = '/nfs/slac/g/atlas/u02/cmilke/dihiggs/input/'
gen_file_list = lambda link: [ input_dir+link+'/'+ntuple for ntuple in os.listdir(input_dir+link) ]
datasets = {
     'MC16d_ggF-HH-bbbb'       : gen_file_list('ntuples_MC16d_ggF-HH-bbbb'),
     'MC16d_VBF-HH-bbbb_cvv0'  : gen_file_list('ntuples_MC16d_VBF-HH-bbbb_cvv0'),
     'MC16d_VBF-HH-bbbb_cvv0p5': gen_file_list('ntuples_MC16d_VBF-HH-bbbb_cvv0p5'),
     'MC16d_VBF-HH-bbbb_cvv1'  : gen_file_list('ntuples_MC16d_VBF-HH-bbbb_cvv1'),
     'MC16d_VBF-HH-bbbb_cvv1p5': gen_file_list('ntuples_MC16d_VBF-HH-bbbb_cvv1p5'),
     'MC16d_VBF-HH-bbbb_cvv2'  : gen_file_list('ntuples_MC16d_VBF-HH-bbbb_cvv2'),
     'MC16d_VBF-HH-bbbb_cvv4'  : gen_file_list('ntuples_MC16d_VBF-HH-bbbb_cvv4')
}


input_mc_standard = [
    '/nfs/slac/g/atlas/u02/cmilke/dihiggs/input/user.jagrundy.HH4B.450000.SM_HH.MC16e-2018.AB21.2.91-MAR20-0.full_MiniNTuple.root/user.jagrundy.20736225._000001.MiniNTuple.root',
    '/nfs/slac/g/atlas/u02/cmilke/dihiggs/input/user.jagrundy.HH4B.450000.SM_HH.MC16e-2018.AB21.2.91-MAR20-0.full_MiniNTuple.root/user.jagrundy.20736225._000002.MiniNTuple.root'
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


def etaphi_difference(eta1, phi1, eta2, phi2):
    Deta = eta1 - eta2
    Dphi = phi1 - phi2
    if Dphi > pi: Dphi -= 2*pi
    elif Dphi < -pi: Dphi += 2*pi
    return (Deta,Dphi)
