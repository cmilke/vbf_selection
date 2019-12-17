#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from acorn_backend.plotting_utils import accumulate_performance

_category_key = 'JVT'
_hist_bins = 30
_hist_range = (0,1)


def retrieve_parameter(data_dump, is_bgd, required_quarks, pt_cut):
    parameter_list = []
    weight_list = []

    event_index = 0
    for event in data_dump[is_bgd][_category_key].events:
        if len(event.jets) != 3: continue
        leading_pt = 0.0
        num_quarks = 0
        for jet in event.jets: 
            num_quarks += jet.truth_id in range(1,7)
            leading_pt = max(leading_pt, jet.vector.pt)
        if required_quarks != None and num_quarks != required_quarks: continue
        eta_sorted_jets = sorted(event.jets, key=lambda j: j.vector.eta)
        extra_jet_pt = eta_sorted_jets[1].vector.pt
        if extra_jet_pt > leading_pt*pt_cut: continue

        event_index += 1
        #if event_index >= 100: break

        eta_normalization = eta_sorted_jets[2].vector.eta - eta_sorted_jets[0].vector.eta
        extra_jet_distance_to_leftMost_jet = eta_sorted_jets[1].vector.eta - eta_sorted_jets[0].vector.eta
        colinearity_measure = abs( extra_jet_distance_to_leftMost_jet / eta_normalization - 0.5 ) * 2

        event_weight = event.event_weight
        parameter_list.append(colinearity_measure)
        weight_list.append(event_weight)

    counts, bins = numpy.histogram(parameter_list, weights=weight_list, bins=_hist_bins, range=_hist_range)
    norms = counts / counts.sum()
    performance = accumulate_performance(norms, is_bgd)
    print(event_index)
    return (performance, bins[:-1])


def draw_distribution(data_dump, pt_cut):
    print(pt_cut)
    sig2_norms, sig2_vals = retrieve_parameter(data_dump, 0, 2, pt_cut)
    sig3_norms, sig3_vals = retrieve_parameter(data_dump, 0, 3, pt_cut)
    bgd_norms, bgd_vals = retrieve_parameter(data_dump, 1, None, pt_cut)

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
    plt.xlabel(r'$2*|\frac{\eta_3 - \eta_-}{\eta_+ - \eta_-} - 0.5|$')
    plt.title('Co-linearity Distribution of 3-Jet Events,\nFor Jets with > '+str(pt_cut)+' Leading-Jet $p_T$')
    fig.savefig('plots/figures/fig_eta_co-linearity_monotonic_distribution_'+str(pt_cut)+'.pdf')
    plt.close()
    print()


def draw_all():
    data_dump = [ pickle.load( open('data/output_untagged_sig.p', 'rb') ),
                  pickle.load( open('data/output_untagged_bgd.p', 'rb') ) ]

    draw_distribution(data_dump, 0)
    draw_distribution(data_dump, 0.2)
    draw_distribution(data_dump, 0.5)
    draw_distribution(data_dump, 0.7)
    draw_distribution(data_dump, 0.9)
    draw_distribution(data_dump, 0.99)


draw_all()
