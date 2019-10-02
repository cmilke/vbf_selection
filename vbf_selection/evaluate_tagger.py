#!/usr/bin/env python

import sys
import math
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from acorn_backend import evaluation_filters

_hist_bins = 20

_plot_specifications = {
    2: {
        ''    : ['null']
    },
    3: {
        ''    : ['2maxpt', 'etamax', 'truth', 'random']
      , 'noPU': ['2maxpt', 'etamax']
      , 'withPU': ['2maxpt', 'etamax']
    }
}

_discriminator_titles = {
    'delta_eta': '$\Delta \eta$'
  , 'mjj'      : '$m_{jj}$'
  , 'mjjj'     : '$m_{jjj}$'
}

_event_filters = {
    '': (
        '',
        None
    ),
    'noPU': (
        ' (no PU)',
        evaluation_filters.no_pileup
    ),
    'withPU': (
        ' (with PU)',
        evaluation_filters.with_pileup
    ),
}

_jet_selection_titles = {
    'null'   : ''
  , '2maxpt' : ',\nVBF Jets Chosen by Highest $p_t$'
  , 'etamax' : ',\nVBF Jets Chosen by Maximized $\eta$'
  , 'truth'  : ',\nVBF Jets Chosen at Truth Level'
  , 'random' : ',\nVBF Jets Chosen Randomly'
}

_jet_category_titles = {}
for jet_count, filter_list in _plot_specifications.items():
    for event_filter, selector_list in filter_list.items():
        for selector in selector_list:
            key = str(jet_count)+event_filter+'_'+selector
            label_string = str(jet_count) + ' Jets'
            label_string += _event_filters[event_filter][0]
            label_string += _jet_selection_titles[selector]
            _jet_category_titles[key] = label_string


def filter_events(filter_function, event_list, discriminant_list):
    if filter_function == None: return discriminant_list
    filtered_discriminants = []
    for event, discriminant in zip(event_list, discriminant_list):
        if filter_function(event): filtered_discriminants.append(discriminant)
    return filtered_discriminants
    

def plot_performance(plot_type, tagger_name):
    input_type = 'sig'
    ytitle = 'Efficiency'
    cumulative = -1
    if plot_type == 'rejection':
        input_type = 'bgd'
        ytitle = 'Rejection'
        cumulative = 1

    event_input = pickle.load( open('data/input_'+input_type+'.p', 'rb') )
    tagger_output = pickle.load( open('data/tagged_'+tagger_name+'_'+input_type+'.p', 'rb') )

    # Flatten out the multiply-nested tagger output, so it can be easily visualized
    # We start by copying the _jet_category_titles dict because it ensures the 
    # internal ordering of the key/value pairs in the dict are consistent between
    # the efficiency counts, rejection counts, and labels
    flattened_discriminants = _jet_category_titles.copy()
    for jet_count, selector_dict in enumerate(tagger_output):
        for filter_key in _event_filters.keys():
            for selector_name, discriminant_list in selector_dict.items():
                category_label = str(jet_count)+filter_key+'_'+selector_name
                if category_label not in _jet_category_titles: continue
                event_list = event_input[jet_count]
                filter_function = _event_filters[filter_key][1]
                filtered_discriminant_list = filter_events(filter_function, event_list, discriminant_list)
                flattened_discriminants[category_label] = filtered_discriminant_list


    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist(flattened_discriminants.values(), 
        label=flattened_discriminants.keys(), histtype='step', bins=_hist_bins,
        cumulative=cumulative, density=True, linewidth=3)

    discriminator_name = _discriminator_titles[tagger_name]
    ax.legend( *map(reversed, ax.get_legend_handles_labels()) )
    plt.xlabel(r'Cut on '+discriminator_name)
    plt.ylabel(ytitle)
    plt.title(ytitle+' of '+discriminator_name+'-Based Tagging')
    plt.grid(True)
    fig.savefig('plots/fig_'+tagger_name+'_'+plot_type+'.pdf')
    plt.close()
    return counts


def evaluate_individual_performances(tagger_name): 
    discriminator_name = _discriminator_titles[tagger_name]

    #evaluate efficiency and rejection
    sig_counts = plot_performance('efficiency', tagger_name)
    bgd_counts = plot_performance('rejection', tagger_name)
    
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
    plt.savefig('plots/fig_'+tagger_name+'_roc_efficiency.pdf')
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


all_rocs = {}
#produce individual performance plots
for tagger_name in _discriminator_titles.keys():
    print('Generating plots for ' + tagger_name)
    roc_curves = evaluate_individual_performances(tagger_name)
    all_rocs[tagger_name] = roc_curves


#produce cross-tagger performance plots
for category_label in _jet_category_titles.keys():
    print('Generating cross-tagger plots for '+category_label)
    roc_collection = []
    for tagger, tagger_rocs in all_rocs.items():
        if category_label in tagger_rocs:
            roc_collection.append((tagger_rocs[category_label],tagger))
    plot_cross_tagger_roc(category_label, roc_collection)
