#!/usr/bin/env python

import sys
import math
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from acorn_backend.plotting_utils import retrieve_data, Hist_bins, accumulate_performance


_filename_infix = '_aviv'
#_filename_infix = '_2-3-summary'

_plot_specifications = {
    (2,'JVT','null','mjj') : '2: $M_{jj}$'
  #, (2,'JVT','null','2jetNNtagger') : '2: NN Tagger'
  , (3,'JVT','2maxpt','mjj') : '3: 2 Leading $p_t$ - $M_{jj}$'
  , (3,'JVT','random','mjj') : '3: Random - $M_{jj}$'
  , (3,'JVT','truth','mjj') : '3: Truth - $M_{jj}$'
  , (3,'JVT','mjjmax','mjj') : '3: Max $M_{jj}$ - $M_{jj}$'
  #, (3,'JVT','coLinear-mjj','united-Deta') : '3: Merged $M_{jj}$ - $\Delta \eta$'
  #, (3,'JVT','dummy3jet','3jNNtagger') : '3: NN Direct'
  #, (3,'JVT','pairMLP','mjj') : '3: MLP - $M_{jj}$'
  #, (3,'JVT','mjjmax','2jetNNtagger') : '3: Max $M_{jj}$ - NN Tagger'
  #, (3,'JVT','pairMLP','2jetNNtagger') : '3: MLP - NN Tagger'
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

_key_order = { key:index for index,key in enumerate(_plot_specifications) }


def extract_tagger_information(input_type):
    event_map = retrieve_data(input_type)
    for combination_key, key_list in _performances_to_combine.items():
        value_range = event_map[key_list[0]][0]
        combined_discriminants = []
        combined_weights = []
        for event_key in key_list:
            combined_discriminants += event_map[event_key][1][0]
            combined_weights       += event_map[event_key][1][1]
        data = ( combined_discriminants, combined_weights )
        event_map[combination_key] = ( value_range, data )

    binned_data = [None] * len(_plot_specifications)
    for event_key, (value_range, data) in event_map.items():
        if event_key not in _plot_specifications: continue
        discriminants, weights = data
        group_label = _plot_specifications[event_key]
        plot_index = _key_order[event_key]

        counts, bins = numpy.histogram(discriminants, weights=weights, bins=Hist_bins, range=value_range)
        norms = counts / counts.sum()
        performance = accumulate_performance(norms, input_type == 'bgd')
        binned_data[plot_index] = performance
    return binned_data


def evaluate():
    sig_data = extract_tagger_information('sig')
    bgd_data = extract_tagger_information('bgd')

    #evaluate overall performance
    roc_curves = {}
    roc_ax = plt.subplots()
    for raw_eff,raw_rej,label in zip(sig_data, bgd_data, _plot_specifications.values() ):
        eff = [1] + list(raw_eff)
        rej = [0] + list(raw_rej)
        roc_curves[label] = (eff, rej)
        plt.plot(eff, rej, label=label, linewidth=1)
    
    plt.legend()
    plt.xlabel(r'Signal Efficiency')
    plt.ylabel(r'Background Rejection')
    #plt.xlim(0.2, 0.6)
    #plt.ylim(0.6, 1)
    plt.title(r'Efficiency/Rejection Performance of Various Taggers')
    plt.grid(True)
    plt.savefig('plots/performance/roc'+_filename_infix+'.pdf')
    plt.close()


evaluate()
