#!/usr/bin/env python

import sys
sys.path.append('/nfs/slac/g/atlas/u02/cmilke/analysis/util')
import cmilke_analysis_utils as autils
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

_branch_list = {
    'j0'    : ['tj0pT', 'j0truthid', 'j0_isTightPhoton', 'j0_isPU', 
                        'j0_JVT', 'j0_fJVT_Tight', 'j0pT', 'j0eta', 'j0phi', 'j0m']
}

_hist_bins = 50


def draw_distribution(param_list, hist_range, title, units, file_infix):
    counts, bins = numpy.histogram(param_list, bins=_hist_bins, range=hist_range)
    counts = counts / counts.sum()

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist( bins[:-1], weights=counts,
        bins=_hist_bins, linewidth=3, range=hist_range)

    plt.grid()
    #plt.yscale('log')
    #plt.ylim(10e-6, 1)
    plt.xlabel(title+units)
    plt.title('Distribution of '+title+' for Pileup Jets' )
    fig.savefig('fig_pu_'+file_infix+'_distribution.pdf')
    plt.close()


def record_events(input_type):
    input_list = _input_type_options[input_type]
    eta_list = []
    pt_list = []
    for event in autils.event_iterator(input_list, 'Nominal', _branch_list, 10000, None):
        for rj in autils.jet_iterator(_branch_list['j0'], event['j0']):
            if rj['j0_isTightPhoton']: continue
            if rj['tj0pT'] > 0: continue # We are only looking at pileup jets
            eta_list.append(rj['j0eta'])
            pt_list.append(rj['j0pT'])

    draw_distribution( eta_list, (0,6), r'$\eta$', '', 'eta' )
    draw_distribution( pt_list, (0,100), r'$p_t$', ' (GeV)', 'pt' )


record_events('sig')
