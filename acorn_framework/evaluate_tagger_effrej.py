#!/usr/bin/env python

import sys
import math
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import acorn_backend
from acorn_backend import plotting_utils


_whitelist = {
    (2,'JVT','mjj')
  , (3,'JVT','mjjmax')
  , (3,'JVT','mjj_from_leading_pt')
  , (3,'JVT','mjj_of_random_jets')
 }


def plot_performance(input_type, tagger_key, value_range, binned_data, data_dump_infix):
    if input_type == 'sig':
        ytitle = 'Efficiency'
        cumulative = -1
    else:
        ytitle = 'Rejection'
        cumulative = 1

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist( **binned_data, range=value_range,
        histtype='step', bins=plotting_utils.Hist_bins, cumulative=cumulative, linewidth=1)

    discriminator_name = plotting_utils._tagger_titles[tagger_key]
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


def extract_tagger_information(event_map):
    # Group the same taggers together
    tagger_map = {}
    for event_key, (value_range, data_lists) in sorted( event_map.items() ):
        tagger_key = plotting_utils._tagger_idents[ event_key[-1] ]
        #if event_key in _blacklist: continue
        #if event_key not in _whitelist: continue
        if tagger_key not in tagger_map: tagger_map[tagger_key] = (value_range, {})
        tagger_map[tagger_key][1][event_key] = data_lists

    binned_tagger_map = {}
    for tagger_key, (value_range, group_map) in tagger_map.items():
        binned_data = {'x':[], 'weights':[], 'label':[]}
        for event_key, (discriminants, weights) in group_map.items():
            counts, bins = numpy.histogram(discriminants, weights=weights, bins=plotting_utils.Hist_bins, range=value_range)
            norms = counts / counts.sum()
            binned_data['x'].append(bins[:-1])
            binned_data['weights'].append(norms)
            binned_data['label'].append( plotting_utils.make_title(event_key) )
        binned_tagger_map[tagger_key] = (value_range, binned_data)
    return binned_tagger_map


def plot_input_type(input_type):
    data_dump_infix = sys.argv[1]
    data_file = 'data/output_'+data_dump_infix+'_'+input_type+'.p'
    event_map = plotting_utils.retrieve_data(data_file)
    binned_tagger_map = extract_tagger_information(event_map)
    for tagger_key, (value_range, binned_data) in sorted(binned_tagger_map.items()):
        plot_performance(input_type, tagger_key, value_range, binned_data, data_dump_infix)


plot_input_type('sig')
plot_input_type('bgd')
