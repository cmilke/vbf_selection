#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import sys
import pickle
import itertools
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from acorn_backend.analysis_utils import reload_data

_category_key = 'JVT'
_hist_bins = 100
_hist_range = (0,5000)
_plot_titles = {
   'sig0': 'Signal, $M_{jj}$ Max'
  , 'sig1': 'Signal, $M_{jj}$ Sub-Leading'
  , 'sig2': 'Signal, $M_{jj}$ Minimum'
  , 'bgd0': 'Background, $M_{jj}$ Max'
  , 'bgd1': 'Background, $M_{jj}$ Sub-Leading'
  , 'bgd2': 'Background, $M_{jj}$ Minimum'
}
_events_with_3_jets = {}


def retrieve_parameter(input_type):
    if input_type not in _events_with_3_jets:
        data_dump = pickle.load( open('data/output_'+sys.argv[1]+'_'+input_type+'.p', 'rb') )
        _events_with_3_jets[input_type] = [ event for event in data_dump[_category_key].events if len(event.jets) > 2 ]

    parameter_list = []
    for event in _events_with_3_jets[input_type]:
        mass_pairs = [  (jet_i.vector+jet_j.vector).mass for jet_i,jet_j in itertools.combinations(event.jets, 2) ]
        mass_pairs.sort(reverse=True)
        parameter_list.append(mass_pairs)
    mjj_array = numpy.array(parameter_list)
    return mjj_array


def extract_data():
    extracted_data = {
        'sig': retrieve_parameter('sig')
      , 'bgd': retrieve_parameter('bgd')
    }

    return extracted_data


def draw_distribution(retrieved_data, filename_infix, title_insert, plot_list):
    processed_data = {}
    for label, mjj_array in retrieved_data.items():
        ordered_mjjs = mjj_array.transpose()
        for rank, mjj_list in enumerate(ordered_mjjs):
            key = label+str(rank)
            processed_data[key] = mjj_list

    plot_values = {'x':[],'weights':[],'label':[]}
    for key in plot_list:
        label = _plot_titles[key]
        counts, bins = numpy.histogram(processed_data[key], bins=_hist_bins, range=_hist_range)
        norms = counts / counts.sum()
        plot_values['x'].append( bins[:-1] )
        plot_values['weights'].append(norms)
        plot_values['label'].append(label)

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist(**plot_values, histtype='step', bins=_hist_bins, linewidth=2, range=_hist_range)
    ax.legend()
    plt.grid()
    #plt.yscale('log')
    #plt.ylim(10e-6, 1)
    #plt.ylim(0, 0.2)
    plt.xlim(0, 2000)
    plt.xlabel('$M_{jj}$ (GeV)')
    plt.title('$M_{jj}$ of '+title_insert+' Jet Pairs')
    fig.savefig('plots/figures/mjj'+filename_infix+'_distribution.pdf')
    plt.close()


def draw_all_distributions():
    retrieved_data = reload_data(len(sys.argv) > 2, extract_data, suffix='_'+sys.argv[1])

    draw_distribution(retrieved_data, '_signal', 'Signal', ['sig2','sig1','sig0'])
    draw_distribution(retrieved_data, '_background', 'Background', ['bgd2','bgd1','bgd0'])
    draw_distribution(retrieved_data, '_leading', 'Leading', ['bgd0','sig0'])
    draw_distribution(retrieved_data, '_subleading', 'Sub-leading', ['bgd1','sig1'])
    draw_distribution(retrieved_data, '_minimal', 'Minimum', ['bgd2','sig2'])


draw_all_distributions()
