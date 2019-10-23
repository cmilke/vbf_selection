#!/usr/bin/env python

import sys
import math
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from acorn_backend import event_taggers

_hist_bins = 200

_filename_infix = ''

_plot_specifications = {
    '2JVT_null_mjj'   : ('2 JVT: $M_{jj}$', event_taggers.mjjj_tagger.value_range)
  , '3JVT_truth_mjj'  : ('3 JVT: Truth', event_taggers.mjj_tagger.value_range)
  , '3JVT_mjjXetamax_mjj'  : ('3 JVT: Maximized $\Delta \eta * M_{jj}$ - $M_{jj}$', event_taggers.mjj_tagger.value_range)
  , '3JVT_2maxpt_mjjj' : ('3 JVT: $M_{jjj}$', event_taggers.mjjj_tagger.value_range)
  , '3JVT_etamax_mjj'  : ('3 JVT: Maximized $\Delta \eta$ - $M_{jj}$', event_taggers.mjj_tagger.value_range)
  , '3JVT_2maxpt_mjj'  : ('3 JVT: 2 Max $p_t$ - $M_{jj}$', event_taggers.mjj_tagger.value_range)
}

_performances_to_combine = {
  #  '2JVT_null_mjjj' : '>=2_mjjj'
  #, '3JVT_2maxpt_mjjj': '>=2_mjjj'
  #, '2JVT_null_mjj' : '>=2_mjj'
  #, '3JVT_2maxpt_mjj' : '>=2_mjj'
}



# Retrieves the nested data structure from the specified output file,
# and then restructures the data to be usuable for this analysis
def retrieve_data( input_type ):
    # First, copy the _plot_specifications dict to ensure the internal
    # ordering of the key/value pairs in the dict are consistent between
    # the efficiency counts, rejection counts, and labels
    # Note: "group" is a combination of the jet count, category, selector, and tagger
    group_map = _plot_specifications.copy()
    for key in group_map: group_map[key] = ([],[])

    event_dump = pickle.load( open('data/output_'+input_type+'.p', 'rb') )
    # Flatten out the deeply-nested event dump
    for category in event_dump.values():
        for event in category.events:
            jet_count = len(event.jets)
            event_weight = event.event_weight
            for selector in event.selectors.values():
                for tagger in selector.taggers.values():
                    discriminant = tagger.discriminant
                    group_key = str(jet_count)+category.key+'_'+selector.key+'_'+tagger.key
                    if group_key in group_map:
                        group_map[group_key][0].append(discriminant)
                        group_map[group_key][1].append(event_weight)
                    if group_key in _performances_to_combine:
                        combined_key = _performances_to_combine[group_key]
                        group_map[combined_key][0].append(discriminant)
                        group_map[combined_key][1].append(event_weight)
    return group_map


def extract_tagger_information(input_type):
    group_map = retrieve_data(input_type)

    binned_data = []
    for group_key, (discriminants, weights) in group_map.items():
        group_label = _plot_specifications[group_key][0]
        value_range = _plot_specifications[group_key][1]
        counts, bins = numpy.histogram(discriminants, weights=weights, bins=_hist_bins, range=value_range)
        norms = counts / counts.sum()
        sum_direction = 1 if input_type == 'bgd' else -1
        flip = slice(None,None,sum_direction)
        performance = norms[flip].cumsum()[flip]
        binned_data.append(performance)
    return binned_data


def evaluate():
    sig_data = extract_tagger_information('sig')
    bgd_data = extract_tagger_information('bgd')

    #evaluate overall performance
    roc_curves = {}
    roc_ax = plt.subplots()
    for raw_eff,raw_rej,label in zip(sig_data, bgd_data, [x[0] for x in _plot_specifications.values()] ):
        eff = [1] + list(raw_eff)
        rej = [0] + list(raw_rej)
        roc_curves[label] = (eff, rej)
        plt.plot(eff, rej, label=label, linewidth=1)
    
    plt.legend()
    plt.xlabel(r'Signal Efficiency')
    plt.ylabel(r'Background Rejection')
    plt.title(r'Efficiency/Rejection Performance of Various Taggers')
    plt.grid(True)
    plt.savefig('plots/focused_perf_'+_filename_infix+'roc_efficiency.pdf')
    plt.close()


evaluate()
