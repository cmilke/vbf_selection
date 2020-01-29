#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import sys
import pickle
import random
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from acorn_backend.plotting_utils import accumulate_performance
from acorn_backend.analysis_utils import reload_data

_category_key = 'JVT20'
_data_title = sys.argv[1]

_hist_bins = 200000
_hist_range = (-10000,10000)
#_hist_range = (0,4)

#_hist_range = (1-4,1+4)
#_hist_bins = 2


_data_dump = {}


def extract_input(input_type, method):
    global _data_dump
    if input_type not in _data_dump:
        input_file = 'data/output_'+_data_title+'_record_'+input_type+'.p'
        _data_dump[input_type] = pickle.load( open(input_file, 'rb') )

    parameter_list = []
    print(input_type)
    num_pt_matched = 0
    num_total = 0
    num_crossing = 0
    num_crossing_matched = 0
    for index, event in enumerate( _data_dump[input_type][_category_key].events) :
        #jets_to_use = [ jet for jet in event.jets if not jet.is_pileup ]
        #jets_to_use = [ jet for jet in event.jets if jet.truth_id != -1 ]
        jets_to_use = event.jets
        if len(jets_to_use) != 3: continue

        quark_jets = []
        for jet in jets_to_use: 
            if jet.is_truth_quark(): quark_jets.append(jet)
            else: gluon_jet = jet
        if len(quark_jets) > 2: continue

        if method == 'cheat': # Use quark jets as primaries
            primary_jets = quark_jets
            extra_jet = gluon_jet

        elif method == 'pt': # Use highest pt jets as primaries
            jets = sorted(jets_to_use, key = lambda j:j.vector.pt)
            primary_jets = jets[1:]
            extra_jet = jets[0]

        elif method == 'random': # pick primaries at random
            jets = jets_to_use.copy()
            random.shuffle(jets)
            primary_jets = jets[:2]
            extra_jet = jets[2]

        elif method == 'mjj': # Use highest mjj pair as primaries
            highest_mjj = 0
            primary_jets = None
            extra_jet = None
            jet_permutations = [ (0,1,2), (1,2,0), (2,0,1) ]
            for i,j,k in jet_permutations:
                mjj = (jets_to_use[i].vector + jets_to_use[j].vector).mass
                if mjj > highest_mjj:
                    highest_mjj = mjj
                    primary_jets = [ jets_to_use[i], jets_to_use[j] ]
                    extra_jet = jets_to_use[k]

        elif method == 'forward': # Use most forward jets as primaries
            jets = sorted(jets_to_use, key = lambda j:j.vector.eta)
            primary_jets = [ jets[0],jets[2] ]
            extra_jet = jets[1]

        else:
            exit(2)

        if len(primary_jets) != 2: continue
        #if ( method != 'cheat' and primary_jets[0].is_truth_quark() and primary_jets[1].is_truth_quark() ): continue
        #if not ( primary_jets[0].is_truth_quark() and primary_jets[1].is_truth_quark() ): continue

        num_total += 1
        primary_jets.sort(key=lambda j: j.vector.eta)

        primary_Deta = primary_jets[1].vector.eta - primary_jets[0].vector.eta
        extra_Deta = extra_jet.vector.eta - primary_jets[0].vector.eta
        primary_mjj = (primary_jets[1].vector + primary_jets[0].vector).mass
        parameter_list.append( (primary_Deta, extra_Deta, primary_mjj) )


        #if primary_mjj > 500: num_crossing += 1
        #if ( primary_jets[0].is_truth_quark() and primary_jets[1].is_truth_quark() ):
        #    num_pt_matched += 1
        #    if primary_mjj > 500:
        #        num_crossing_matched += 1
        #elif primary_mjj > 500:
        #    quark_Deta = quark_jets[1].vector.eta - quark_jets[0].vector.eta
        #    gluon_Deta = gluon_jet.vector.eta - quark_jets[0].vector.eta
        #    f1 = abs(extra_Deta / primary_Deta)
        #    f2 = abs(gluon_Deta / quark_Deta)
        #    print( '{:.02}/{:.02} ; {:.02}/{:.02} ; ( {:.02}, {:.02} )'.format(extra_Deta, primary_Deta, gluon_Deta, quark_Deta, f1,f2) )

    #print(num_total, num_pt_matched, num_crossing, num_crossing_matched)
    print(num_total)
    return(parameter_list)


def extract_data():
    retrieved_data_dictionary = {
        #'sigC': extract_input('sig','cheat')
       'sigpt': extract_input('sig','pt')
      #, 'sigR': extract_input('sig','random')
      #, 'sigF': extract_input('sig','forward')
      #, 'sigM': extract_input('sig','mjj')
        #'bgd': extract_input('bgd',method)
    }
    return retrieved_data_dictionary


def draw_distribution(retrieved_data_dictionary, mjj_cut):
    plot_values = {'x':[], 'weights':[], 'label':[]}
    titles = {
        'sigC': 'Sig - Quarks'
      , 'sigpt': 'Sig - $p_T$'
      , 'sigR': 'Sig - Random'
      , 'sigF': 'Sig - Forward'
      , 'sigM': 'Sig - $M_{jj}$'
      , 'bgd': 'Bgd - Forward'
    }

    for key, retrieved_data in retrieved_data_dictionary.items():
        parameter_list = [ 2*(extra/primary-0.5) for primary,extra,mjj in retrieved_data if mjj > mjj_cut]
        counts, bins = numpy.histogram(parameter_list, bins=_hist_bins, range=_hist_range)
        print(key, counts.sum())
        norms = counts / counts.sum()

        plot_values['x'].append(bins[:-1])
        plot_values['weights'].append(norms)
        plot_values['label'].append(titles[key])

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist( **plot_values, histtype='step', bins=_hist_bins, linewidth=2, range=_hist_range)
    plt.axvline(x=1, color='black')
    plt.axvline(x=-1, color='black')

    #ax.legend(loc='upper center')
    ax.legend()
    plt.grid()

    plt.ylim(0, 0.04)
    #plt.ylim(0, 1)
    plt.xlim(-3, 3)

    plt.xlabel(r'$2 \times (\frac{\eta_3 - \eta_{q-}}{\eta_{q+} - \eta_{q-}} - 0.5)$')
    #plt.title('Co-linearity Distribution of 3-Jet Events,\nFor Lowest $p_T$ Jets with $p_T$ > '+str(mjj_cut))
    plt.title('Co-linearity Distribution of 3-Jet Events,\nWith Primary $M_{jj}$ > '+str(mjj_cut)+' and All $p_T$ > 20')
    fig.savefig('plots/figures/colinearity_'+_data_title+'_mjj_'+str(mjj_cut)+'.pdf')
    plt.close()


def draw_all():
    retrieved_data = reload_data(len(sys.argv) > 2, extract_data, suffix='_'+_data_title)

    draw_distribution(retrieved_data, 0)
    draw_distribution(retrieved_data, 500)

draw_all()
