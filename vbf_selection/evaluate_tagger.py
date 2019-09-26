import sys
import math
import pickle
import numpy
from matplotlib import pyplot as plt


def plot_performance(input_dict, plot_type, discriminator_name, bins, labels):
    ytitle = 'Efficiency'
    cumulative = -1
    if plot_type == 'rejection':
        ytitle = 'Rejection'
        cumulative = 1

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist(input_dict.values(), 
        label=labels, histtype='step', bins=bins,
        cumulative=cumulative, density=True, linewidth=3)

    ax.legend( *map(reversed, ax.get_legend_handles_labels()) )
    plt.xlabel(r'Cut on '+discriminator_name+' of Two Leading-$p_t$ Jets')
    plt.ylabel(ytitle)
    plt.title(ytitle+' of '+discriminator_name+'-Based Tagging')
    plt.grid(True)
    fig.savefig('plots/fig_'+plot_type+'.pdf')
    return counts


tagger_output_sig = pickle.load( open('data/tagged_sig.p', 'rb') )
tagger_output_bgd = pickle.load( open('data/tagged_bgd.p', 'rb') )

bins = numpy.arange(0,8,0.1)
labels = list(tagger_output_sig)

discriminator_name = '$\Delta \eta$'

#evaluate efficiency and rejection
sig_counts = plot_performance(tagger_output_sig, 'efficiency', discriminator_name, bins, labels)
bgd_counts = plot_performance(tagger_output_bgd, 'rejection', discriminator_name, bins, labels)


#evaluate overall performance
roc_ax = plt.subplots()
for x,y,label in zip(sig_counts, bgd_counts, labels):
    plt.plot(x, y, label=label)

plt.legend()
plt.xlabel(r'Signal Efficiency')
plt.ylabel(r'Background Rejection')
plt.title(r'Efficiency/Rejection Performance of'+discriminator_name+'-Based Tagging')
plt.grid(True)
plt.savefig('plots/roc_efficiency.pdf')

#plt.show()
