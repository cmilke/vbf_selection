#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

_selector_key = '2maxpt'
_hist_bins = 100
_hist_range = (0,5000)


def retrieve_parameter(category_key):
    input_type = 'sig'
    parameter_list = []
    weight_list = []

    data_dump = pickle.load( open('data/output_'+input_type+'.p', 'rb') )
    event_index = 0
    for event in data_dump[category_key].events:
        #if event_index >= 20: break
        if len(event.jets) != 3: continue
        event_index += 1

        selector = event.selectors[_selector_key]
        mjjj = event.selectors[_selector_key].taggers['mjjj'].discriminant
        event_weight = event.event_weight
        parameter_list.append(mjjj)
        weight_list.append(event_weight)

    counts, bins = numpy.histogram(parameter_list, weights=weight_list, bins=_hist_bins, range=_hist_range)
    norms = counts / counts.sum()
    return (counts, bins[:-1])


def draw_distribution():
    all_norms, all_vals = retrieve_parameter('all')
    noPU_norms, noPU_vals = retrieve_parameter('noPU')
    JVT_norms, JVT_vals = retrieve_parameter('JVT')

    norms = ( all_norms, noPU_norms, JVT_norms)
    vals = ( all_vals, noPU_vals, JVT_vals)

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist( vals, weights=norms,
        label=('All'
             , 'No Pileup'
             , 'JVT Filter'),
        histtype='step', bins=_hist_bins, linewidth=2, range=_hist_range)

    ax.legend()
    plt.grid()
    #plt.yscale('log')
    #plt.ylim(10e-6, 1)
    plt.xlabel('$M_{jjj}$ (GeV)')
    plt.title('$M_{jjj}$ Distribution Across Several Event Categories')
    fig.savefig('plots/fig_mjjj_3-jet_distribution.pdf')
    plt.close()


draw_distribution()
