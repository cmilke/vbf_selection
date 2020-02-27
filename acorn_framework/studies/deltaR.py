#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import sys
import pickle
import random
import math
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from acorn_backend.analysis_utils import reload_data

_category_key = 'JVT'
_data_title = sys.argv[1]

_hist_bins = 20
_hist_range = (0,10)
#_hist_range = (0,4)

#_hist_range = (1-4,1+4)
#_hist_bins = 2

_events_with_3_jets = {}


def extract_input(input_type, selection_key):
    global _events_with_3_jets
    if input_type not in _events_with_3_jets:
        input_file = 'data/output_'+_data_title+'_tag_'+input_type+'.p'
        data_dump = pickle.load( open(input_file, 'rb') )
        _events_with_3_jets[input_type] = [ event for event in data_dump[_category_key].events if len(event.jets) > 2 ]

    parameter_list = []
    for event in _events_with_3_jets[input_type]:
        selections = event.selectors[selection_key].selections
        extra_index = ({0,1,2} - set(selections[:2])).pop()
        primary_vectors = [ event.jets[ selections[0] ].vector, event.jets[ selections[0] ].vector ]
        extra_vector = event.jets[ extra_index ].vector

        delta_R_list = [ vec.delta_r(extra_vector) for vec in primary_vectors ]
        delta_R_list.sort()
        parameter_list.append(delta_R_list[0]) 
    return(parameter_list)


def extract_data():
    retrieved_data_dictionary = {
        'sigC': extract_input('sig','truth')
      , 'sigpt': extract_input('sig','2maxpt')
      , 'sigM': extract_input('sig','mjjmax')
      , 'sigF': extract_input('sig','etamax')
      , 'bgdpt': extract_input('bgd','2maxpt')
      , 'bgdM': extract_input('bgd','mjjmax')
      , 'bgdF': extract_input('bgd','etamax')
    }
    return retrieved_data_dictionary


def draw_distribution(retrieved_data_dictionary, mjj_cut):
    plot_values = {'x':[], 'weights':[], 'label':[]}
    titles = {
      #  'sigC':  'Sig - Quarks'
        'sigpt': 'Sig - $p_T$'
      , 'sigF': 'Sig - $p_T$'
      , 'bgdpt': 'Bgd - $\Delta \eta_{max}$'
      , 'bgdF': 'Bgd - $\Delta \eta_{max}$'
      #, 'sigM': 'Sig - $M_{jj}$'
      #, 'bgdM': 'Bgd - $M_{jj}$'
    }

    for key, retrieved_data in retrieved_data_dictionary.items():
        if key not in titles: continue
        parameter_list = retrieved_data

        counts, bins = numpy.histogram(parameter_list, bins=_hist_bins, range=_hist_range)
        print(key, counts.sum())
        norms = counts / counts.sum()
        #norms = counts

        plot_values['x'].append(bins[:-1])
        plot_values['weights'].append(norms)
        plot_values['label'].append(titles[key])

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist( **plot_values, histtype='step', bins=_hist_bins, linewidth=2, range=_hist_range)

    #ax.legend(loc='upper center')
    ax.legend(prop={'size':8})
    plt.grid()

    #plt.yscale('log')
    #plt.ylim(0, 1)
    #plt.xlim(0, 10)

    plt.xlabel('$\Delta R$ Between Extra Jet and Closest Primary Jet')
    plt.title('$\Delta R$ Distribution of 3-Jet Events')
    fig.savefig('plots/figures/deltaR_'+_data_title+'_mjj'+str(mjj_cut)+'.pdf')
    plt.close()


def draw_all():
    retrieved_data = reload_data(len(sys.argv) > 2, extract_data, suffix='_'+_data_title)

    draw_distribution(retrieved_data, 0)
    #draw_distribution(retrieved_data, 500)

draw_all()
