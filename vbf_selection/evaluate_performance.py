import sys
import math
import pickle
import numpy
from matplotlib import pyplot as plt

tagger_output_sig = pickle.load( open('data/tagged_sig_truth.p', 'rb') )
tagger_output_bgd = pickle.load( open('data/tagged_bgd_truth.p', 'rb') )

bins = numpy.arange(0,8,0.1)
labels = list(tagger_output_sig)
for i in range(len(labels)): labels[i] = str(labels[i])+' Jets'

#evaluate efficiency
sig_fig,sig_ax = plt.subplots()
sig_counts, sig_bins, sig_hist = plt.hist(list(tagger_output_sig.values()), 
    label=labels, histtype='step', bins=bins,
    cumulative=-1, density=True, linewidth=3)

sig_ax.legend( *map(reversed, sig_ax.get_legend_handles_labels()) )
plt.xlabel(r'Cut on $\Delta \eta$ of Two Leading-$p_t$ Jets')
plt.ylabel(r'Efficiency')
plt.title(r'Efficiency of $\Delta \eta$-Based Tagging')
plt.grid(True)
sig_fig.savefig('plots/fig_efficiency.pdf')


#evaluate background rejection
bgd_fig,bgd_ax = plt.subplots()
bgd_counts, bgd_bins, bgd_hist = plt.hist(list(tagger_output_bgd.values()), 
    label=labels, histtype='step', bins=bins,
    cumulative=1, density=True, linewidth=3)

bgd_ax.legend( *map(reversed, bgd_ax.get_legend_handles_labels()) )
plt.xlabel(r'Cut on $\Delta \eta$ of Two Leading-$p_t$ Jets')
plt.ylabel(r'Rejection')
plt.title(r'Rejection of $\Delta \eta$-Based Tagging')
plt.grid(True)
bgd_fig.savefig('plots/bgd_efficiency.pdf')


#evaluate overall performance
roc_ax = plt.subplots()
plt.plot(sig_counts[0], bgd_counts[0], label='2-Jets')
plt.plot(sig_counts[1], bgd_counts[1], label='3-Jets')

plt.legend()
plt.xlabel(r'Signal Efficiency')
plt.ylabel(r'Background Rejection')
plt.title(r'Efficiency/Rejection Performance of $\Delta \eta$-Based Tagging')
plt.grid(True)
plt.savefig('plots/roc_efficiency.pdf')


#plt.show()
