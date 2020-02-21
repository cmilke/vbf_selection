#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import sys
import pickle
import numpy
from itertools import combinations
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from acorn_backend.analysis_utils import reload_data

_mjj_bin_count = 8
_mjj_max = 1000
_mjj_ticks = range(0,_mjj_bin_count**3,_mjj_bin_count*2)
_label_range = range(0,_mjj_max, int(_mjj_max/_mjj_bin_count))
_all_labels = [ (i,j) for i in _label_range for j in _label_range ]
_mjj_labels = [ label for label in _all_labels[::2] ]

_Nevents = 10000
_events_with_3_jets = None
_category_key = 'JVT'


def retrieve_parameter(input_type, mjj_cut):
    global _events_with_3_jets

    if _events_with_3_jets == None:
        data_dump = pickle.load( open('data/output_aviv_tag_'+input_type+'.p', 'rb') )
        _events_with_3_jets = [ event for event in data_dump[_category_key].events if len(event.jets) > 2 ]

    mjj_possiblities_list = []
    for event in _events_with_3_jets:
        mjj_list = [ (i.vector+j.vector).mass for i,j in combinations(event.jets, 2) ]
        mjj_list.sort(reverse=True)
        mjj_possiblities_list.append(mjj_list)

    return mjj_possiblities_list


def extract_data():
    extracted_data = {
        'Signal': retrieve_parameter('sig', 0)
      , 'Background': retrieve_parameter('bgd', 0)
    }

    return extracted_data


def draw_mjj(retrieved_data):

    plot_values = {'x':[],'weights':[],'label':[]}
    for label, mjj_possiblities_list in retrieved_data.items():
        if label == 'Signal': continue
        mjj_array = numpy.clip( numpy.array(mjj_possiblities_list), 0, _mjj_max)
        hist3d, edges = numpy.histogramdd( mjj_array, bins=_mjj_bin_count, range=[(0,_mjj_max)]*3 )
        flat_hist = hist3d.flatten()
        flat_edges = [ (i,j,k) for i in edges[0][:-1] for j in edges[1][:-1] for k in edges[2][:-1] ]

        plot_values['x'].append( list(range(len(flat_edges))) )
        plot_values['weights'].append(flat_hist)
        plot_values['label'].append(label)


    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist( **plot_values, histtype='bar', bins=_mjj_bin_count**3, linewidth=1, range=(0,_mjj_bin_count**3) )

    ax.legend(loc='upper center')
    plt.grid()
    plt.xticks(ticks=_mjj_ticks, labels=_mjj_labels, rotation=90, fontsize=4)
    #plt.yscale('log')
    #plt.ylim(10e-6, 1)
    #plt.ylim(0, 0.2)
    #plt.xlim(0, 2000)
    plt.xlabel('Leading, Sub-Leading, (Sub-Sub-Leading) $M_{jj}$ of Events')
    plt.title('')
    plt.tight_layout()
    fig.savefig('plots/figures/mjj_pair_distribution.pdf')
    plt.close()


def draw_distributions():
    retrieved_data = reload_data(len(sys.argv) > 1, extract_data)
    draw_mjj(retrieved_data)

draw_distributions()
