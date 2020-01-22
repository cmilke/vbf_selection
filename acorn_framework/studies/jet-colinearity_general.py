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


_data_dump = {}


def extract_input(input_type):
    global _data_dump
    if input_type not in _data_dump:
        #input_file = 'data/output_aviv_truth_record_'+input_type+'.p'
        input_file = 'data/output_cmilkeV1_truth_record_'+input_type+'.p'
        #input_file = 'data/output_aviv_record_'+input_type+'.p'
        _data_dump[input_type] = pickle.load( open(input_file, 'rb') )

    parameter_list = []
    print(input_type)
    num_useful_events = 0
    for event in _data_dump[input_type][_category_key].events:
        if len(event.jets) != 3: continue
        num_real_jets = 0
        for jet in event.jets:
            if jet.truth_id > 0: num_real_jets += 1
            #if not jet.is_pileup: num_real_jets += 1
            #num_real_jets += 1
        if num_real_jets > 2: num_useful_events += 1


        # Use quark jets as primaries
        #if False: 
        if input_type == 'sig':
            primary_jets = []
            for jet in event.jets: 
                if jet.truth_id in range(1,7): primary_jets.append(jet)
                else: extra_jet = jet
        else:
            # Use highest mjj pair as primaries
            #jets = sorted(event.jets, key = lambda j:j.vector.pt)
            highest_mjj = 0
            primary_jets = None
            extra_jet = None
            jet_permutations = [ (0,1,2), (1,2,0), (2,0,1) ]
            for i,j,k in jet_permutations:
                mjj = (event.jets[i].vector + event.jets[j].vector).mass
                if mjj > highest_mjj:
                    highest_mjj = mjj
                    primary_jets = [ event.jets[i], event.jets[j] ]
                    extra_jet = event.jets[k]

        # Use highest pt jets as primaries
        #jets = sorted(event.jets, key = lambda j:j.vector.pt)
        #primary_jets = jets[1:]
        #extra_jet = jets[0]

        # Use most forward jets as primaries
        #jets = sorted(event.jets, key = lambda j:j.vector.eta)
        #primary_jets = [ jets[0],jets[2] ]
        #extra_jet = jets[1]

        if len(primary_jets) != 2: continue
        primary_jets.sort(key=lambda j: j.vector.eta)

        primary_Deta = primary_jets[1].vector.eta - primary_jets[0].vector.eta
        extra_Deta = extra_jet.vector.eta - primary_jets[0].vector.eta
        parameter_list.append( (primary_Deta, extra_Deta, extra_jet.vector.pt) )

    print(num_useful_events)
    return(parameter_list)


def extract_data():
    retrieved_data_dictionary = {
        'sig - quarks': extract_input('sig'),
        'bgd - $M_{jj}$ Max': extract_input('bgd')
    }
    return retrieved_data_dictionary


def draw_distribution(retrieved_data_dictionary, pt_cut):
    plot_values = {'x':[], 'weights':[], 'label':[]}

    for key, retrieved_data in retrieved_data_dictionary.items():
        parameter_list = [ 2*(extra/primary-0.5) for primary,extra,pt in retrieved_data ]
        counts, bins = numpy.histogram(parameter_list, bins=_hist_bins, range=_hist_range)
        norms = counts / counts.sum()

        plot_values['x'].append(bins[:-1])
        plot_values['weights'].append(norms)
        plot_values['label'].append(key)

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist( **plot_values, histtype='step', bins=_hist_bins, linewidth=2, range=_hist_range)
    plt.axvline(x=1, color='black')
    plt.axvline(x=-1, color='black')

    #ax.legend(loc='upper center')
    ax.legend()
    plt.grid()
    #plt.yscale('log')
    #plt.ylim(10e-6, 1)
    #plt.ylim(0, 0.35)
    plt.xlabel(r'$2 \times (\frac{\eta_3 - \eta_{q-}}{\eta_{q+} - \eta_{q-}} - 0.5)$')
    #plt.title('Co-linearity Distribution of 3-Jet Events,\nFor Lowest $p_T$ Jets with $p_T$ > '+str(pt_cut))
    plt.title('Co-linearity Distribution of 3-Jet Events,\nWith $p_T$ > '+str(pt_cut))
    fig.savefig('plots/figures/colinearity_pt_'+str(pt_cut)+'.pdf')
    plt.close()


def draw_all():
    retrieved_data = reload_data(len(sys.argv) > 1, extract_data)

    draw_distribution(retrieved_data, 30)

draw_all()
