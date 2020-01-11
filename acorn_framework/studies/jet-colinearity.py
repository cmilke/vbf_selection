#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import sys
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from acorn_backend.plotting_utils import accumulate_performance
from acorn_backend.analysis_utils import reload_data

_category_key = 'JVT'
_hist_bins = 100
_hist_range = (-3,3)


def extract_data():
    data_dump = pickle.load( open('data/output_aviv_record_sig.p', 'rb') )

    parameter_list = []
    for event in data_dump[_category_key].events:
        if len(event.jets) != 3: continue
        # Use quark jets as primaries
        #primary_jets = []
        #for jet in event.jets: 
        #    if jet.truth_id in range(1,7): primary_jets.append(jet)
        #    else: extra_jet = jet

        # Use highest pt jets as primaries
        jets = sorted(event.jets, key = lambda j:j.vector.pt)
        primary_jets = jets[1:]
        extra_jet = jets[0]

        # Use most forward jets as primaries
        #jets = sorted(event.jets, key = lambda j:j.vector.eta)
        #primary_jets = [ jets[0],jets[2] ]
        #extra_jet = jets[1]

        if len(primary_jets) != 2: continue
        primary_jets.sort(key=lambda j: j.vector.eta)

        primary_Deta = primary_jets[1].vector.eta - primary_jets[0].vector.eta
        extra_Deta = extra_jet.vector.eta - primary_jets[0].vector.eta
        parameter_list.append( (primary_Deta, extra_Deta, extra_jet.vector.pt) )
    return(parameter_list)


def draw_distribution(pt_cut):
    retrieved_data = reload_data(len(sys.argv) > 1, extract_data)

    parameter_list = [ 2*(extra/primary-0.5) for primary,extra,pt in retrieved_data ]
    counts, bins = numpy.histogram(parameter_list, bins=_hist_bins, range=_hist_range)
    norms = counts / counts.sum()
    #performance = accumulate_performance(norms, False)

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist( bins[:-1], weights=norms,
        histtype='step', bins=_hist_bins, linewidth=2, range=_hist_range)
    plt.axvline(x=1, color='black')
    plt.axvline(x=-1, color='black')

    #ax.legend(loc='upper center')
    #ax.legend()
    plt.grid()
    #plt.yscale('log')
    #plt.ylim(10e-6, 1)
    #plt.ylim(0, 0.35)
    plt.xlabel(r'$2 \times (\frac{\eta_g - \eta_{q-}}{\eta_{q+} - \eta_{q-}} - 0.5)$')
    plt.title('Co-linearity Distribution of 3-Jet Events,\nFor Gluon Jets with $p_T$ > '+str(pt_cut))
    fig.savefig('plots/figures/colinearity_pt_'+str(pt_cut)+'.pdf')
    plt.close()


def draw_all():
    draw_distribution(30)

draw_all()
