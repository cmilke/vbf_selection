#!/usr/bin/env python

import sys
import math
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from acorn_backend.event_taggers import tagger_class_list

_hist_bins = 50

_plot_specifications = {
    2: {
        '': ['null']
    },
    3: {
        ''      : ['2maxpt', 'etamax', 'truth', 'random']
      , 'noPU'  : ['2maxpt', 'etamax']
      , 'withPU': ['2maxpt', 'etamax']
    }
}

_discriminator_titles = {
    'Deta': '$\Delta \eta$'
  , 'mjj'      : '$m_{jj}$'
  , 'mjjj'     : '$m_{jjj}$'
}

_filter_titles = {
    '': ''
  , 'noPU': ' (no PU)'
  , 'withPU': ' (with PU)'
}

_jet_selection_titles = {
    'null'   : ''
  , '2maxpt' : ',\nVBF Jets Chosen by Highest $p_t$'
  , 'etamax' : ',\nVBF Jets Chosen by Maximized $\eta$'
  , 'truth'  : ',\nVBF Jets Chosen at Truth Level'
  , 'random' : ',\nVBF Jets Chosen Randomly'
}


def make_group_key(jet_count, category_key, selector_key):
    return str(jet_count)+category_key+'_'+selector_key

_jet_category_titles = {}
for jet_count, filter_list in _plot_specifications.items():
    for event_filter, selector_list in filter_list.items():
        for selector in selector_list:
            key = make_group_key(jet_count, event_filter, selector)
            label_string = str(jet_count) + ' Jets'
            label_string += _filter_titles[event_filter]
            label_string += _jet_selection_titles[selector]
            _jet_category_titles[key] = label_string


def plot_performance(input_type, tagger_name, group_map):
    discriminant_map = group_map[input_type][tagger_name]

    if input_type == 'sig':
        ytitle = 'Efficiency'
        cumulative = -1
    else:
        ytitle = 'Rejection'
        cumulative = 1

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist(discriminant_map.values(), 
        label=discriminant_map.keys(), histtype='step', bins=_hist_bins,
        cumulative=cumulative, density=True, linewidth=3)

    discriminator_name = _discriminator_titles[tagger_name]
    ax.legend( *map(reversed, ax.get_legend_handles_labels()) )
    plt.xlabel(r'Cut on '+discriminator_name)
    plt.ylabel(ytitle)
    plt.title(ytitle+' of '+discriminator_name+'-Based Tagging')
    plt.grid(True)
    fig.savefig('plots/fig_'+tagger_name+'_'+ytitle+'.pdf')
    plt.close()
    return counts


def evaluate_individual_performances(tagger_key, group_map): 
    discriminator_name = _discriminator_titles[tagger_key]

    #evaluate efficiency and rejection
    sig_counts = plot_performance('sig', tagger_key, group_map)
    bgd_counts = plot_performance('bgd', tagger_key, group_map)
    
    #evaluate overall performance
    roc_curves = {}
    roc_ax = plt.subplots()
    for raw_eff,raw_rej,label in zip(sig_counts, bgd_counts, _jet_category_titles.keys()):
        eff = [1] + list(raw_eff)
        rej = [0] + list(raw_rej)
        roc_curves[label] = (eff, rej)
        plt.plot(eff, rej, label=label)
    
    plt.legend()
    plt.xlabel(r'Signal Efficiency')
    plt.ylabel(r'Background Rejection')
    plt.title(r'Efficiency/Rejection Performance of '+discriminator_name+'-Based Tagging')
    plt.grid(True)
    plt.savefig('plots/fig_'+tagger_key+'_roc_efficiency.pdf')
    plt.close()
    return roc_curves


def plot_cross_tagger_roc(category_label, roc_collection): 
    roc_ax = plt.subplots()
    for xy, label in roc_collection:
        plt.plot(*xy, label=label)
    
    plt.legend()
    plt.xlabel(r'Signal Efficiency')
    plt.ylabel(r'Background Rejection')
    category_title = _jet_category_titles[category_label]
    plt.title(r'Tagger Performance for Events with '+category_title)
    plt.grid(True)
    plt.savefig('plots/fig_allTaggers_'+category_label+'_roc_efficiency.pdf')
    plt.close()



def extract_discriminants(input_type, output_map):
    # We copy the _jet_category_titles dict because it ensures the 
    # internal ordering of the key/value pairs in the dict are consistent between
    # the efficiency counts, rejection counts, and labels
    new_tagger_map = {}
    for tagger_class in tagger_class_list:
        group_map = _jet_category_titles.copy()
        new_tagger_map[tagger_class.key] = group_map
        for key in group_map.keys(): group_map[key] = []

    event_dump = pickle.load( open('data/output_'+input_type+'.p', 'rb') )
    # Flatten out the deeply-nested event dump, so it can be easily visualized
    for category in event_dump:
        for event in category.events:
            jet_count = len(event.jets)
            for selector in event.selectors:
                for tagger in selector.taggers:
                    discriminant = tagger.discriminant
                    group_key = make_group_key(jet_count, category.key, selector.key)
                    if group_key in _jet_category_titles:
                        new_tagger_map[tagger.key][group_key].append(discriminant)

    output_map[input_type] = new_tagger_map


def evaluate():
    output_map = {}
    extract_discriminants('sig', output_map)
    extract_discriminants('bgd', output_map)

    #produce individual performance plots
    all_rocs = {}
    for tagger_key in _discriminator_titles.keys():
        print('Generating plots for ' + tagger_key)
        roc_curves = evaluate_individual_performances(tagger_key, output_map)
        all_rocs[tagger_key] = roc_curves


    #produce cross-tagger performance plots
    for category_label in _jet_category_titles.keys():
        print('Generating cross-tagger plots for '+category_label)
        roc_collection = []
        for tagger, tagger_rocs in all_rocs.items():
            if category_label in tagger_rocs:
                roc_collection.append((tagger_rocs[category_label],tagger))
        plot_cross_tagger_roc(category_label, roc_collection)


evaluate()
