#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def get_counts(data_dump, category_key, jet_count):
    total_events = 0
    for event in data_dump[category_key].events:
        if len(event.jets) == jet_count: total_events += 1
    return total_events
    

def draw(input_type):
    data_dump = pickle.load( open('data/output_'+input_type+'.p', 'rb') )
    xlabels = [
        '2 Jets, $p_t > 30$ GeV'
      , '3 Jets, $p_t > 30$ GeV'
      , '3 Jets, $p_t > 40$ GeV'
    ]
    num_bins = len(xlabels)

    vals = {
        'x': [i for i in range(num_bins)],
        'weights': [
            get_counts(data_dump, 'JVT', 2)
          , get_counts(data_dump, 'JVT', 3)
          , get_counts(data_dump, 'JVTpt40', 3)
        ]
    }
    print(vals)

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist( **vals, bins=num_bins, range=(0,num_bins) )

    input_title = 'Signal' if input_type == 'sig' else 'Background'
    plt.title('Number of '+input_title+' Events for Various Category Restrictions')
    plt.xticks(ticks=(bins+0.5), labels=xlabels, rotation=45, fontsize='xx-small', horizontalalignment='center')
    ax.set_xticks(bins, minor=True)
    ax.xaxis.grid(True, which='minor')
    ax.yaxis.grid(True)
    plt.tight_layout()
    #plt.show()
    fig.savefig('plots/figures/fig_eventCounts_'+input_type+'.pdf')
    plt.close()


draw('sig')
draw('bgd')
