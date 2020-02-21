#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import sys
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from acorn_backend.analysis_utils import reload_data

_category_key = 'JVT'
_selector_key = '2maxpt'
_hist_bins = 50
_Nevents = 10000
_events_with_3_jets = {}
_max_parameter_size = 100

def retrieve_parameter(input_type, deep_filter_key):
    global _events_with_3_jets

    eta0_list = []
    eta1_list = []
    weight_list = []

    if input_type not in _events_with_3_jets:
        data_dump = pickle.load( open('data/output_aviv_tag_'+input_type+'.p', 'rb') )
        _events_with_3_jets[input_type] = [ event for event in data_dump[_category_key].events if len(event.jets) > 2 ]

    for event in _events_with_3_jets[input_type]:
        selector = event.selectors[_selector_key]
        if deep_filter_key in selector.deep_filters:
            eta0 = event.jets[selector.selections[0]].vector.eta
            eta1 = event.jets[selector.selections[1]].vector.eta
            eta0_list.append(eta0)
            eta1_list.append(eta1)
            weight_list.append(event.event_weight)
            #if len(eta0) > _max_parameter_size: break

    return (eta0_list, eta1_list, weight_list)


def extract_data():
    extracted_data = {
        'Any': retrieve_parameter('sig', 'any')
      , '$M_{jj}>500$': retrieve_parameter('sig', 'mjj500')
    }

    return extracted_data


def draw_raw_etas(retrieved_data):
    hist_range = (-4,4)

    plot_values = {'x':[],'weights':[],'label':[]}
    for label, (eta0_list, eta1_list, weight_list) in retrieved_data.items():
        parameter_list = eta0_list + eta1_list
        double_weights = weight_list + weight_list
        counts, bins = numpy.histogram(parameter_list, weights=double_weights, bins=_hist_bins, range=hist_range)
        norms = counts / counts.sum()
        plot_values['x'].append( bins[:-1] )
        plot_values['weights'].append(norms)
        plot_values['label'].append(label)


    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist( **plot_values, histtype='step', bins=_hist_bins, linewidth=2, range=hist_range)

    ax.legend(loc='upper center')
    plt.grid()
    #plt.yscale('log')
    #plt.ylim(10e-6, 1)
    #plt.ylim(0, 0.2)
    #plt.xlim(0, 2000)
    plt.xlabel('$\eta$')
    plt.title('$\eta$ Distribution of Leading Two Jets')
    fig.savefig('plots/figures/leading_eta_distribution.pdf')
    plt.close()


def draw_Delta_eta(retrieved_data):
    hist_range = (0,8)
    plot_values = {'x':[],'weights':[],'label':[]}
    for label, (eta0_list, eta1_list, weight_list) in retrieved_data.items():
        parameter_list = [ abs(eta0-eta1) for eta0, eta1 in zip(eta0_list, eta1_list) ]
        counts, bins = numpy.histogram(parameter_list, weights=weight_list, bins=_hist_bins, range=hist_range)
        norms = counts / counts.sum()
        plot_values['x'].append( bins[:-1] )
        plot_values['weights'].append(norms)
        plot_values['label'].append(label)


    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist( **plot_values, histtype='step', bins=_hist_bins, linewidth=2, range=hist_range)

    ax.legend(loc='upper right')
    plt.grid()
    #plt.yscale('log')
    #plt.ylim(10e-6, 1)
    #plt.ylim(0, 0.2)
    #plt.xlim(0, 2000)
    plt.xlabel('$\Delta \eta$')
    plt.title('$\Delta \eta$ Distribution of Leading Two Jets')
    fig.savefig('plots/figures/leading_Delta_eta_distribution.pdf')
    plt.close()


def draw_distributions():
    retrieved_data = reload_data(len(sys.argv) > 1, extract_data)
    draw_raw_etas(retrieved_data)
    draw_Delta_eta(retrieved_data)

draw_distributions()
