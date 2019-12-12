#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

_category_key = 'JVT'
_hist_bins = 30
_hist_range = (0,1)


def retrieve_parameter(input_type, required_quarks):
    parameter_list = []
    weight_list = []

    data_dump = pickle.load( open('data/output_'+input_type+'.p', 'rb') )
    event_index = 0
    for event in data_dump[_category_key].events:
        if len(event.jets) != 3: continue
        if required_quarks != None:
            num_quarks = 0
            for jet in event.jets: 
                if jet.truth_id in range(1,7): num_quarks += 1
            if num_quarks != required_quarks: continue
        event_index += 1
        #if event_index >= 100: break

        eta_list = [ jet.vector.eta for jet in event.jets ]
        eta_list.sort()

        eta_normalization = eta_list[2] - eta_list[0]
        extra_jet_distance_to_leftMost_jet = eta_list[1] - eta_list[0]
        colinearity_measure = extra_jet_distance_to_leftMost_jet / eta_normalization

        event_weight = event.event_weight
        parameter_list.append(colinearity_measure)
        weight_list.append(event_weight)

    counts, bins = numpy.histogram(parameter_list, weights=weight_list, bins=_hist_bins, range=_hist_range)
    norms = counts / counts.sum()
    print(event_index)
    return (norms, bins[:-1])


def draw_distribution():
    sig2_norms, sig2_vals = retrieve_parameter('sig', 2)
    sig3_norms, sig3_vals = retrieve_parameter('sig', 3)
    bgd_norms, bgd_vals = retrieve_parameter('bgd', None)

    plot_inputs = {
        'x': (sig2_vals, sig3_vals, bgd_vals),
        'weights': (sig2_norms, sig3_norms, bgd_norms),
        'label': ('Signal 2-Quarks', 'Signal 3-Quarks', 'Background')
    }

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist( **plot_inputs,
        histtype='step', bins=_hist_bins, linewidth=2, range=_hist_range)

    ax.legend(loc='upper center')
    plt.grid()
    #plt.yscale('log')
    #plt.ylim(10e-6, 1)
    #plt.ylim(0, 0.35)
    plt.xlabel(r'$\frac{\eta_3 - \eta_-}{\eta_+ - \eta_-}$')
    plt.title('Co-linearity Distribution of 3-Jet Events')
    fig.savefig('plots/figures/fig_eta_co-linearity_distribution.pdf')
    plt.close()


draw_distribution()
