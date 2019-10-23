#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

_category_key = 'JVT'
_selector_key = 'mjjmax'
_hist_bins = 20
_hist_range = (1,2)


def retrieve_parameter(input_type):
    parameter_list = []
    weight_list = []

    data_dump = pickle.load( open('data/output_'+input_type+'.p', 'rb') )
    event_index = 0
    for event in data_dump[_category_key].events:
        #if event_index >= 20: break
        if len(event.jets) != 3: continue
        event_index += 1

        selector = event.selectors[_selector_key]
        mjj = event.selectors[_selector_key].taggers['mjj'].discriminant
        mjjj = event.selectors[_selector_key].taggers['mjjj'].discriminant
        event_weight = event.event_weight
        parameter_list.append(mjjj/mjj)
        weight_list.append(event_weight)

    counts, bins = numpy.histogram(parameter_list, weights=weight_list, bins=_hist_bins, range=_hist_range)
    norms = counts / counts.sum()
    return (norms, bins[:-1])


def draw_distribution():
    sig_norms, sig_vals = retrieve_parameter('sig')
    bgd_norms, bgd_vals = retrieve_parameter('bgd')

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist( (sig_vals, bgd_vals),
        weights=(sig_norms, bgd_norms),
        label=('Signal', 'Background'), histtype='step',
        bins=_hist_bins, linewidth=2, range=_hist_range)

    ax.legend()
    plt.grid()
    #plt.yscale('log')
    #plt.ylim(10e-6, 1)
    plt.xlabel('$M_{jjj}$/ Maximized $M_{jj}$')
    plt.title(r'$M_{jjj}/M_{jj}$ Distribution of 3-Jet Signal (VBF->H->$\gamma\gamma$)''\n'
            r'and Background (ggF->H->$\gamma\gamma$) Events')
    fig.savefig('plots/fig_mjjj-mjj-ratio_3-jet_distribution.pdf')
    plt.close()


draw_distribution()
