#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

_category_key = 'JVT'
_hist_bins = 100
_hist_range = (0,5000)
_tagger_titles = {
    'mjj': '$M_{jj}$'
  , 'mjjj': '$M_{jjj}$'
}
_selector_titles = {
    'null': ''
  , '2maxpt': ' of the Leading 2 Jets'
  , 'mjjmax': ' of the 2 Jets Which Maximize $M_{jj}$'
}


def retrieve_parameter(input_type, selector_key, tagger_key):
    parameter_list = []
    weight_list = []

    data_dump = pickle.load( open('data/output_aviv_tag_'+input_type+'.p', 'rb') )
    event_index = 0
    for event in data_dump[_category_key].events:
        #if event_index >= 20: break
        #if len(event.jets) != 3: continue
        if len(event.jets) != 2: continue
        event_index += 1

        selector = event.selectors[selector_key]
        mjj = event.selectors[selector_key].taggers[tagger_key].discriminant
        event_weight = event.event_weight
        parameter_list.append(mjj)
        weight_list.append(event_weight)

    counts, bins = numpy.histogram(parameter_list, weights=weight_list, bins=_hist_bins, range=_hist_range)
    norms = counts / counts.sum()
    return (norms, bins[:-1])


def draw_distribution(selector_key, tagger_key):
    sig_norms, sig_vals = retrieve_parameter('sig', selector_key, tagger_key)
    bgd_norms, bgd_vals = retrieve_parameter('bgd', selector_key, tagger_key)

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist( (sig_vals, bgd_vals),
        weights=(sig_norms, bgd_norms),
        label=('Signal', 'Background'), histtype='step',
        bins=_hist_bins, linewidth=2, range=_hist_range)

    ax.legend()
    plt.grid()
    plt.yscale('log')
    plt.ylim(10e-6, 1)
    #plt.ylim(0, 0.35)
    plt.xlabel('$M_{jj}$ (GeV)')
    tagger_title = _tagger_titles[tagger_key]
    selector_title = '' if tagger_key == 'mjjj' else _selector_titles[selector_key]
    plt.title(tagger_title+' Distribution'+selector_title)
    fig.savefig('plots/figures/fig_mjj_'+selector_key+'_'+tagger_key+'_distribution.pdf')
    plt.close()


#draw_distribution('2maxpt', 'mjj')
#draw_distribution('mjjmax', 'mjj')
#draw_distribution('2maxpt', 'mjjj')
draw_distribution('null', 'mjj')
