import sys
import math
import pickle
import numpy
from matplotlib import pyplot as plt

tagger_output_sig = pickle.load( open('data/tagged_signal_truth.p', 'rb') )
#tagger_output_bgd = pickle.load( open('data/outputs_background_truth.p', 'rb') )

#evaluate efficiency
sig_fig,sig_ax = plt.subplots()
bins = numpy.arange(0,8,0.1)
labels = list(tagger_output_sig)
for i in range(len(labels)): labels[i] = str(labels[i])+' Jets'

sig_counts, sig_bins, sig_hist = plt.hist(list(tagger_output_sig.values()), 
    label=labels, histtype='step', bins=bins,
    cumulative=-1, density=True, linewidth=3)

sig_ax.legend( *map(reversed, sig_ax.get_legend_handles_labels()) )
plt.xlabel(r'Cut on $\Delta \eta$ of Two Leading-$p_t$ Jets')
plt.ylabel(r'Efficiency')
plt.title(r'Efficiency of Basic Tagging')
plt.grid(True)
plt.show()

#print( len(tagger_output) )


#evaluate background rejection



#evaluate overall performance
