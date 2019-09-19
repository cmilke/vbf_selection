import pickle
import numpy
from matplotlib import pyplot as plt

availability = pickle.load( open('availability.p', 'rb') )
xlabels = [
      'No Limits'
    , '$\geq$2 Truth Jets\n$p_t>20$GeV'
    , '$\geq$3 Truth Jets\n$p_t>20$GeV'
    , '$\geq$2\nnon-$\gamma$\nTruth Jets'
    , '$\geq$3\nnon-$\gamma$\nTruth Jets'
    , '$\geq$2\nq-Matched\nTruth Jets'
    , '$\geq$3\nq-Matched\nTruth Jets'
    #, '2 Outgoing\nQuarks'
    #, '2 Valid\nTruth Jets'
    #, '>=3 Valid\nTruth Jets'
    #, '$\geq$ 2\nReco Jets'
    #, 'Not\ntightPhoton'
    #, 'Not\nPileup'
    #, 'Passes\n$p_t$/$\eta$ Cuts'
    #, '$\geq$ 2\nValid Jets'
    #, '$\geq$ 3\nValid Jets'
    #, '$\geq$ 4\nValid Jets'
    #, '$\geq$ 5\nValid Jets'
    #, '$\geq$ 6\nValid Jets'
]
bins = numpy.arange(0,len(xlabels)+1,1)

fig,ax = plt.subplots()
counts, bins, hist = plt.hist(availability, bins=bins, density=False, cumulative=-1)

plt.title('Availability of Events for Successive Restrictions')
plt.xticks(ticks=(bins+0.5), labels=xlabels, rotation=45, fontsize='xx-small', horizontalalignment='center')
ax.set_xticks(bins, minor=True)
ax.xaxis.grid(True, which='minor')
ax.yaxis.grid(True)
plt.tight_layout()
plt.show()
fig.savefig('fig_availability.pdf')
