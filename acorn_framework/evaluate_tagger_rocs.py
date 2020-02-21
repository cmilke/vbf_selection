#!/usr/bin/env python

import sys
import math
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from acorn_backend.plotting_utils import retrieve_data, Hist_bins, accumulate_performance


#_filename_suffix = '_2-3-summary'
_filename_suffix = ''

_plot_specifications = {
    (2,'JVT','null', 'any','mjj') : '2: $M_{jj}$'
  #, (3,'JVT','truth', 'any','mjj') : '3: Harsh Truth - $M_{jj}$'
  , (3,'JVT','mjjSL', 'any','mjj') : '3: $M_{jj}-SL$ - $M_{jj}$'
  , (3,'JVT','mjjmax', 'any','mjj') : '3: Max $M_{jj}$ - $M_{jj}$'
  , (3,'JVT','dummy3jet', 'any','mjjj') : '3: $M_{jjj}$'
  , (3,'JVT','dummy3jet', 'any','Fcentrality') : '3: Forward Centrality'
  , (3,'JVT','2maxpt', 'any','mjj') : '3: Leading $p_t$ - $M_{jj}$'
  , (3,'JVT','mjjmax', 'any','centrality') : '3: Max $M_{jj}$ - Centrality'
  , (3,'JVT','2maxpt', 'any','centrality') : '3: Leading $p_t$ - Centrality'
  , (3,'JVT','random', 'any','mjj') : '3: Random - $M_{jj}$'
  #, (3,'JVT','mjjFantasy', 'any','mjj') : '3: Fantasy - $M_{jj}$'
  #, (3,'JVT','mjjSSL', 'any','mjj') : '3: Min $M_{jj}$ - $M_{jj}$'
  #, (3,'JVT','truth', 'any','mjj') : '3: Truth - $M_{jj}$'
  #, (3,'JVT','truth','Deta') : '3: Truth - $\Delta \eta$'
  #, (3,'JVT','pairMLP','mjj') : '3: MLP - $M_{jj}$'
  #, (2,'JVT','null', 'mjj500','mjj') : '2: $M_{jj} > 500$ GeV - $M_{jj}$'
  #, (3,'JVT','mjjmax', 'mjj500','mjj') : '3: Max $M_{jj}$, $M_{jj} > 500$ GeV - $M_{jj}$'
  #, (3,'JVT','random', 'mjj500','mjj') : '3: Rand, $M_{jj} > 500$ GeV - $M_{jj}$'
  #, '>=2_pt' : '$\geq 2$: Leading $p_t$ - $M_{jj}$'
  #  '>=2_mjj' : '$\geq 2$: Maximized $M_{jj}$ - $M_{jj}$'
  #, '>=2_NN' : '$\geq 2$: Dedicated NNs'
  #, '>=2_NN/mjj' : '$\geq 2$: Maximized $M_{jj}$ - NN'
}

_performances_to_combine = {
  #  '>=2_mjj': [
  #      (2,'JVT','null','mjj')
  #    , (3,'JVT','mjjmax','mjj')
  #  ]
  #, '>=2_NN/mjj': [
  #      (2,'JVT','null','2jetNNtagger')
  #    , (3,'JVT','mjjmax','2jetNNtagger')
  #  ]
  #, '>=2_NN': [
  #      (2,'JVT','null','2jetNNtagger')
  #    , (3,'JVT','dummy3jet','3jNNtagger')
  #  ]
}


def extract_tagger_information(input_type, data_dump_infix):
    data_file = 'data/output_'+data_dump_infix+'_'+input_type+'.p'
    event_map = retrieve_data(data_file)
    for combination_key, key_list in _performances_to_combine.items():
        value_range = event_map[key_list[0]][0]
        combined_discriminants = []
        combined_weights = []
        for event_key in key_list:
            combined_discriminants += event_map[event_key][1][0]
            combined_weights       += event_map[event_key][1][1]
        data = ( combined_discriminants, combined_weights )
        event_map[combination_key] = ( value_range, data )

    for key in _plot_specifications:
        if key not in event_map:
            raise LookupError( str(key) + ' IS EMPTY!\n'
                 '             Did you include this in your tagging list or make a typo?')

    binned_data = {}
    for event_key, (value_range, data) in event_map.items():
        if event_key not in _plot_specifications: continue
        discriminants, weights = data

        counts, bins = numpy.histogram(discriminants, weights=weights, bins=Hist_bins, range=value_range)
        norms = counts / counts.sum()
        performance = accumulate_performance(norms, input_type == 'bgd')

        binned_data[event_key] = performance
    return binned_data


def evaluate():
    data_dump_infix = sys.argv[1]
    sig_data = extract_tagger_information('sig', data_dump_infix)
    bgd_data = extract_tagger_information('bgd', data_dump_infix)

    #evaluate overall performance
    roc_curves = {}
    roc_ax = plt.subplots()
    for event_key, label in _plot_specifications.items():
        #eff = [1] + list(sig_data[event_key])
        #rej = [0] + list(bgd_data[event_key])
        eff = sig_data[event_key]
        rej = bgd_data[event_key]
        roc_curves[label] = (eff, rej)
        #plt.plot(eff, rej, marker='.',label=label, linewidth=1)
        plt.plot(eff, rej, label=label, linewidth=1)
    
    plt.legend(prop={'size':7})
    plt.xlabel(r'Signal Efficiency')
    plt.ylabel(r'Background Rejection')
    #plt.xlim(0.2, 0.6)
    #plt.ylim(0.6, 1)
    plt.title(r'Efficiency/Rejection Performance of Various Taggers')
    plt.grid(True)
    plt.savefig('plots/performance/roc'+'_'+data_dump_infix+_filename_suffix+'.pdf')
    plt.close()


evaluate()
