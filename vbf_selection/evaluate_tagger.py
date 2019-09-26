import sys
import math
import pickle
import numpy
from matplotlib import pyplot as plt

_discriminator_titles = {
    'delta_eta': '$\Delta \eta$'
  , 'mjj'      : '$m_{jj}$'
  #, 'mjjj'     : '$m_{jjj}$'
}

_jet_selection_titles = {
    '2_2maxpt': '2 Jets,\nVBF Jets Chosen by Highest $p_t$'
  , '3_2maxpt': '3 Jets,\nVBF Jets Chosen by Highest $p_t$'
  , '3inclPU_2maxpt':  '3 Jets (incl. PU),\nVBF Jets Chosen by Highest $p_t$'
}
    

def plot_performance(input_dict, plot_type, tagger_name, labels):
    ytitle = 'Efficiency'
    cumulative = -1
    if plot_type == 'rejection':
        ytitle = 'Rejection'
        cumulative = 1

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist(input_dict.values(), 
        label=labels, histtype='step', bins=50,
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
    tagger_output_sig = pickle.load( open('data/tagged_'+tagger_name+'_sig.p', 'rb') )
    tagger_output_bgd = pickle.load( open('data/tagged_'+tagger_name+'_bgd.p', 'rb') )
    labels = list(tagger_output_sig)
    
    #evaluate efficiency and rejection
    sig_counts = plot_performance(tagger_output_sig, 'efficiency', tagger_name, labels)
    bgd_counts = plot_performance(tagger_output_bgd, 'rejection', tagger_name, labels)
    
    #evaluate overall performance
    roc_curves = {}
    roc_ax = plt.subplots()
    for raw_eff,raw_rej,label in zip(sig_counts, bgd_counts, labels):
        eff = [1] + list(raw_eff)
        rej = [0] + list(raw_rej)
        roc_curves[label] = (eff, rej)
        plt.plot(eff, rej, label=label)
    
    plt.legend()
    plt.xlabel(r'Signal Efficiency')
    plt.ylabel(r'Background Rejection')
    plt.title(r'Efficiency/Rejection Performance of'+discriminator_name+'-Based Tagging')
    plt.grid(True)
    plt.savefig('plots/fig_'+tagger_name+'_roc_efficiency.pdf')
    plt.close()
    return roc_curves


def plot_cross_tagger_roc(selector_label, roc_collection): 
    roc_ax = plt.subplots()
    for xy, label in roc_collection:
        plt.plot(*xy, label=label)
    
    plt.legend()
    plt.xlabel(r'Signal Efficiency')
    plt.ylabel(r'Background Rejection')
    selector_title = _jet_selection_titles[selector_label]
    plt.title(r'Tagger Performance for Events with '+selector_title)
    plt.grid(True)
    plt.savefig('plots/fig_allTaggers_'+selector_label+'_roc_efficiency.pdf')
    plt.close()


all_rocs = {}
#produce individual performance plots
for tagger_name in _discriminator_titles.keys():
    roc_curves = evaluate_individual_performances(tagger_name)
    all_rocs[tagger_name] = roc_curves


#produce cross-tagger performance plots
for selector_label in _jet_selection_titles.keys():
    roc_collection = []
    for tagger, tagger_rocs in all_rocs.items():
        if selector_label in tagger_rocs:
            roc_collection.append((tagger_rocs[selector_label],tagger))
    plot_cross_tagger_roc(selector_label, roc_collection)
