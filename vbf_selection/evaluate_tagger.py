import sys
import math
import pickle
import numpy
from matplotlib import pyplot as plt


def plot_performance(plot_type, discriminator_name):
    ytitle = 'Efficiency'
    cumulative = -1
    if plot_type == 'rejection':
        ytitle = 'Rejection'
        cumulative = 1

    sig_fig,sig_ax = plt.subplots()
    sig_counts, sig_bins, sig_hist = plt.hist(tagger_output_sig[min_jets:max_jets], 
        label=labels, histtype='step', bins=bins,
        cumulative=cumulative, density=True, linewidth=3)

    sig_ax.legend( *map(reversed, sig_ax.get_legend_handles_labels()) )
    plt.xlabel(r'Cut on '+discriminator_name+' of Two Leading-$p_t$ Jets')
    plt.ylabel(ytitle)
    plt.title(ytitle+' of '+discriminator_name+'-Based Tagging')
    plt.grid(True)
    sig_fig.savefig('plots/fig_'+plot_type+'.pdf')


tagger_output_sig = pickle.load( open('data/tagged_sig.p', 'rb') )
tagger_output_bgd = pickle.load( open('data/tagged_bgd.p', 'rb') )

min_jets = 2
max_jets = 4 #not inclusive

bins = numpy.arange(0,8,0.1)
labels = list( range(min_jets, max_jets) )
for i in range(len(labels)): labels[i] = str(labels[i])+' Jets'

discriminator_name = '$\Delta \eta$'

#evaluate efficiency and rejection
plot_performance('efficiency', discriminator_name)
plot_performance('rejection', discriminator_name)


#evaluate overall performance
roc_ax = plt.subplots()
plt.plot(sig_counts[0], bgd_counts[0], label='2-Jets')
plt.plot(sig_counts[1], bgd_counts[1], label='3-Jets')

plt.legend()
plt.xlabel(r'Signal Efficiency')
plt.ylabel(r'Background Rejection')
plt.title(r'Efficiency/Rejection Performance of'+discriminator_name+'-Based Tagging')
plt.grid(True)
plt.savefig('plots/roc_efficiency.pdf')

#plt.show()
