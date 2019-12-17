#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import pickle
#import numpy
#import matplotlib
#matplotlib.use('Agg')
#from matplotlib import pyplot as plt
#from matplotlib.backends.backend_pdf import PdfPages
    

def draw(input_type):
    data_dump = pickle.load( open('data/output_untagged_'+input_type+'.p', 'rb') )

    # Yes, this is a silly way to do this, but I was having fun. If you can't follow it, just rewrite it from scratch. It should only take you 5 min.

    events_with_3_jets = [ event for event in data_dump['JVT'].events if len(event.jets) == 3 ]
    # Number of 3-jet events with at least 1 pileup jet
    print(  [ True in [jet.is_pileup for jet in event.jets] for event in events_with_3_jets ].count(True) / len(events_with_3_jets)  )

    # Number of 3-jet events where a pileup jet is the lowest pt jet
    print(  [ sorted(event.jets,key=lambda j: j.vector.pt)[0].is_pileup for event in events_with_3_jets ].count(True) / len(events_with_3_jets) )

    #xlabels = [
    #    '2 Jets, $p_t > 30$ GeV'
    #  , '3 Jets, $p_t > 30$ GeV'
    #]
    #num_bins = len(xlabels)

    #jet_counts = [ len(event.jets) for event in data_dump['JVT'].events ]
    #vals = {
    #    'x': [i for i in range(num_bins)],
    #    'weights': [
    #        jet_counts.count(2),
    #        jet_counts.count(3)
    #    ]
    #}
    #print(vals)

    #fig,ax = plt.subplots()
    #counts, bins, hist = plt.hist( **vals, bins=num_bins, range=(0,num_bins) )

    #input_title = 'Signal' if input_type == 'sig' else 'Background'
    #plt.title('Number of '+input_title+' Events for Various Category Restrictions')
    #plt.xticks(ticks=(bins+0.5), labels=xlabels, rotation=45, fontsize='xx-small', horizontalalignment='center')
    #ax.set_xticks(bins, minor=True)
    #ax.xaxis.grid(True, which='minor')
    #ax.yaxis.grid(True)
    #plt.tight_layout()
    ##plt.show()
    #fig.savefig('plots/figures/fig_eventCounts_'+input_type+'.pdf')
    #plt.close()


draw('sig')
print()
draw('bgd')
