#!/usr/bin/env python

import acorn_backend.analysis_utils as autils
from acorn_backend.uproot_wrapper import event_iterator
import math
import numpy
import pickle
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

#Define all the high level root stuff: ntuple files, branches to be used
_input_type_options = {
    'sig': autils.Flavntuple_list_VBFH125_gamgam[:1],
    'bgd': autils.Flavntuple_list_ggH125_gamgam[:1]
}

_branch_list = [
    ('j0', ['tj0pT', 'j0truthid', 'j0_isTightPhoton', 'j0_isPU', 
                        'j0_JVT', 'j0_fJVT_Tight', 'j0pT', 'j0eta', 'j0phi', 'j0m']
    )
]


def draw_distribution(file_infix, filter_title, unbinned_data):
    pt_bins = (20,30,40,50,100000)
    eta_bins = numpy.arange(0,6,6/50)
    counts, xedges, yedges = numpy.histogram2d( *unbinned_data, bins=(pt_bins, eta_bins) )
    prepared_data = { 'x': [], 'weights': [], 'label': [] }
    for i, pt_cut in enumerate(xedges[:-1]):
        prepared_data['x'].append(yedges[:-1])
        prepared_data['weights'].append(counts[i:].sum(0)) # The pt binning is cumulative
        prepared_data['label'].append( '$p_t > $'+str(pt_cut)+' GeV' )

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist(**prepared_data, bins=eta_bins, linewidth=3, histtype='step')

    plt.grid()
    plt.legend()
    #plt.yscale('log')
    #plt.ylim(10e-6, 1)
    plt.xlabel(r'$|\eta|$')
    plt.title('Distribution of $|\eta|$ for ' + filter_title)
    fig.savefig('fig_'+file_infix+'_distribution.pdf')
    plt.close()


def record_events(input_type, categories):
    input_list = _input_type_options[input_type]
    for event in event_iterator(input_list, 'Nominal', _branch_list, 10000):
        for rj in event['j0']:
            is_pu = rj['tj0pT'] < 0
            is_vbf = rj['j0truthid'] in autils.PDG['quarks']
            passes_jvt = rj['j0_JVT'] and rj['j0_fJVT_Tight']
            for key, value in categories[input_type].items():
                if key[0] and rj['j0_isTightPhoton']: continue
                if key[1] and not is_pu: continue
                if key[2] and not is_vbf: continue
                if key[3] and not passes_jvt: continue
                value[2][0].append(rj['j0pT'])
                value[2][1].append(rj['j0eta'])


def init_storage():
    return ([],[])


def make_distros():
    categories = {
        'sig': {
            (1,0,0,0): ( 'sig', 'Signal Jets', init_storage() )
          , (1,1,0,0): ( 'sig_PU', 'Signal Pileup Jets', init_storage() )
          , (1,1,0,1): ( 'sig_PUwithJVT', 'Signal Pileup Jets filtered by JVT', init_storage() )
          , (1,0,1,0): ( 'sig_VBF', 'Signal VBF Jets', init_storage() )
          , (1,0,0,1): ( 'sig_JVT', 'Signal Jets with JVT Applied', init_storage() )
          , (0,0,0,1): ( 'sig_with_photons', 'Signal Jets Including Photons', init_storage() )
        },
        'bgd': {
            (1,0,0,0): ( 'bgd', 'Background Jets', init_storage() )
          , (1,0,0,1): ( 'bgd_JVT', 'Background Jets with JVT Applied', init_storage() )
          , (1,1,0,0): ( 'bgd_PU', 'Background Pileup Jets', init_storage() )
        }
    }
    record_events('sig', categories)
    record_events('bgd', categories)

    print('Drawing Plots')
    for data in categories.values():
        for key, val in data.items():
            draw_distribution(*val)

make_distros()
