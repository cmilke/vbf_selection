#!/usr/bin/env python

import sys
import math
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from acorn_backend.plotting_utils import retrieve_data, Hist_bins


_whitelist = {
    (2,'JVT','null', 'any','mjj')
  , (3,'JVT','truth', 'any','mjj')
  , (3,'JVT','mjjmax', 'any','mjj')
  , (3,'JVT','mjjSL', 'any','mjj')
  , (3,'JVT','mjjSSL', 'any','mjj')
  , (3,'JVT','2maxpt', 'any','mjj')
  , (3,'JVT','dummy3jet', 'any','mjjj')
  , (3,'JVT','dummy3jet', 'any','Fcentrality')
  , (3,'JVT','mjjmax', 'any','centrality')
  , (3,'JVT','mjjSL', 'any','centrality')
  , (3,'JVT','2maxpt', 'any','centrality')
}


_discriminator_titles = {
    'Deta' : '$\Delta \eta$'
  , 'mjj'  : '$m_{jj}$'
  , 'mjjj' : '$m_{jjj}$'
  , 'centrality' : 'Centrality'
  , '2jetNNtagger' : '2-Jet NN LLR Value'
  , '3jNNtagger' : '3-Jet NN LLR Value'
  , 'Fcentrality' : 'Forward-Based Centrality'
}

_filter_titles = {
    'all': '(No Filters)'
  , 'noPU': ' (no PU)'
  , 'withPU': ' (w/PU)'
  , 'JVT': ' (w/JVT)'
  , 'JVTpt40': ' (w/JVT, $p_t$ > 40 GeV)'
  , 'PtEtaV1JVT': r' ($\Delta \eta_{leading jets} > 2$ w/JVT)'
}

_jet_selection_titles = {
    'null'       : ''
  , 'dummy2jet'  : ''
  , 'dummy3jet'  : ''
  , '2maxpt'     : ',\nVBF Jets Chosen by Highest $p_t$'
  , 'etamax'     : ',\nVBF Jets Chosen by Maximized $\Delta\eta$'
  , 'mjjXetamax' : ',\nVBF Jets Chosen by Maximizing $\Delta\eta * M_{jj}$'
  , 'mjjmax'     : ',\nVBF Jets Chosen by Maximized $M_{jj}$'
  , 'Rmax'       : ',\nVBF Jets Chosen by Maximized $\Delta R$'
  , 'truth'      : ',\nVBF Jets Chosen at Truth Level'
  , 'random'     : ',\nVBF Jets Chosen Randomly'
}


def plot_performance(input_type, tagger_key, value_range, binned_data, data_dump_infix):
    if input_type == 'sig':
        ytitle = 'Efficiency'
        cumulative = -1
    else:
        ytitle = 'Rejection'
        cumulative = 1

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist(binned_data['bins'], 
        weights=binned_data['weights'], label=binned_data['labels'], range=value_range,
        histtype='step', bins=Hist_bins, cumulative=cumulative, linewidth=1)

    discriminator_name = _discriminator_titles[tagger_key]
    #plt.xscale('log')
    legend_location = 'lower right' if input_type == 'bgd' else 'upper right'
    ax.legend(loc=legend_location, prop={'size':7})
    #ax.legend()
    plt.xlabel(r'Cut on '+discriminator_name)
    plt.ylabel(ytitle)
    plt.title(ytitle+' of '+discriminator_name+'-Based Tagging')
    plt.grid(which='both', axis='both')
    fig.savefig('plots/performance/perf_'+data_dump_infix+'_'+tagger_key+'_'+ytitle+'.pdf')
    plt.close()
    return counts


def make_group_label( event_key ):
    return str(event_key[0]) + ': ' + event_key[1] + ' - ' + event_key[2] + ', ' + event_key[3]


def extract_tagger_information(event_map):
    # Group the same taggers together
    tagger_map = {}
    for event_key, (value_range, data_lists) in sorted( event_map.items() ):
        tagger_key = event_key[4]
        #if event_key in _blacklist: continue
        #if event_key not in _whitelist: continue
        if tagger_key not in tagger_map: tagger_map[tagger_key] = (value_range, {})
        tagger_map[tagger_key][1][event_key] = data_lists

    binned_tagger_map = {}
    for tagger_key, (value_range, group_map) in tagger_map.items():
        binned_data = {'bins':[], 'weights':[], 'labels':[]}
        for event_key, (discriminants, weights) in group_map.items():
            counts, bins = numpy.histogram(discriminants, weights=weights, bins=Hist_bins, range=value_range)
            norms = counts / counts.sum()
            binned_data['bins'].append(bins[:-1])
            binned_data['weights'].append(norms)
            binned_data['labels'].append( make_group_label(event_key) )
        binned_tagger_map[tagger_key] = (value_range, binned_data)
    return binned_tagger_map


def plot_input_type(input_type):
    data_dump_infix = sys.argv[1]
    data_file = 'data/output_'+data_dump_infix+'_'+input_type+'.p'
    event_map = retrieve_data(data_file)
    binned_tagger_map = extract_tagger_information(event_map)
    for tagger_key, (value_range, binned_data) in sorted(binned_tagger_map.items()):
        plot_performance(input_type, tagger_key, value_range, binned_data, data_dump_infix)


plot_input_type('sig')
plot_input_type('bgd')
