from math import pi
import os


sample_list = [
    'MC16d_ggF-HH-bbbb',
    'MC16d_VBF-HH-bbbb_cvv0', 'MC16d_VBF-HH-bbbb_cvv0p5',
    'MC16d_VBF-HH-bbbb_cvv1', 'MC16d_VBF-HH-bbbb_cvv1p5',
    'MC16d_VBF-HH-bbbb_cvv2', 'MC16d_VBF-HH-bbbb_cvv4'
]

minintuple_dir = '../mini_ntuples/'
gen_file_list = lambda link: [ input_dir+link+'/'+ntuple for ntuple in os.listdir(input_dir+link) ]
MiniNtuples = { sample:gen_file_list('ntuples_'+sample) for sample in sample_list }

nanontuple_dir = '../nano_ntuples/V5/'
NanoNtuples = { sample:[output_dir+'output_'+sample+'.root'] for sample in sample_list }
NanoNtuples['test'] = ['../output/test.root']


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


def etaphi_difference(eta1, phi1, eta2, phi2):
    Deta = eta1 - eta2
    Dphi = phi1 - phi2
    if Dphi > pi: Dphi -= 2*pi
    elif Dphi < -pi: Dphi += 2*pi
    return (Deta,Dphi)
