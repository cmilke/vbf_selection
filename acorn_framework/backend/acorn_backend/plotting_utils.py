import pickle

import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

Hist_bins = 200


# Used by the retrieve_data function to deal with the intricacies of 
# dumping valies into the data map
def fill_event_map(event_map, event_key, tagger, event_weight):
    discriminant = tagger.discriminant
    value_range = tagger.__class__.value_range

    if discriminant < value_range[0]:
        discriminant = value_range[0]
    if discriminant > value_range[1]:
        discriminant = value_range[1] - (value_range[1] - value_range[0])/Hist_bins

    if event_key not in event_map: event_map[event_key] = ( value_range, ([],[]) )
    event_map[event_key][1][0].append(discriminant)
    event_map[event_key][1][1].append(event_weight)


# Retrieves the nested data structure from the specified output file,
# and then restructures the data to be usuable for this analysis
def retrieve_data( data_file ):
    event_map = {}
    event_dump = pickle.load( open(data_file, 'rb') )
    for category in event_dump.values():
        for event in category.events:
            jet_count = len(event.jets)
            event_weight = event.event_weight
            for selector in event.selectors.values():
                for deep_filter in selector.deep_filters.values():
                    for tagger in deep_filter.taggers.values():
                        event_key = (jet_count, category.key, selector.key, deep_filter.key, tagger.key)
                        fill_event_map(event_map, event_key, tagger, event_weight)
    return event_map


def accumulate_performance(distro, is_bgd):
        sum_direction = 1 if is_bgd else -1
        flip = slice(None,None,sum_direction)
        performance = distro[flip].cumsum()[flip]
        return performance


_category_titles = {
    'minimal': ' w/o JVT'
  , 'JVT': ''
  , 'JVT_50-30': ' 50,30,30'
  , 'JVT_70-50-30': ' 70,50,30'
}

_selector_titles = {
    'null'     : ''
  , 'truth'    : ': Harsh Truth'
  , 'mjjSL'    : ': $M_{jj-SL}$'
  , 'mjjmax'   : ': Max $M_{jj}$'
  , '2maxpt'   : ': Leading $p_t$'
  , 'dummy3jet': ''
  , 'random'   : ': Random'
  , 'pairMLP'  : ': pairMLP'
}

_deep_filter_titles = {
    'any': ''
  , 'mjj500': ', $M_{jj} > 500$ GeV'
  , 'central>1': ', C > 1' 
  , 'central<1': ', C < 1' 
}

_tagger_titles = {
    'mjj': ' - $M_{jj}$'
  , 'Deta': ' - $\Delta \eta$'
  , 'centrality': ' - Centrality'
  , 'Fcentrality': ' - Forward Centrality'
  , 'mjjj': ' - $M_{jjj}$'
  , '3jNNtagger': ' - 3 Jet Direct NNv1'
  , '3jNNtaggerV2': ' - 3 Jet Direct NNv2'
  , '3jNNtaggerV3': ' - 3 Jet Direct NNv3'
}


def make_title(event_key):
    num_title = str(event_key[0])
    category_title = _category_titles[ event_key[1] ]
    selector_title = _selector_titles[ event_key[2] ]
    deep_filter_title = _deep_filter_titles[ event_key[3] ]
    tagger_title = _tagger_titles[ event_key[4] ]

    title = num_title+category_title
    title += selector_title+deep_filter_title+tagger_title

    return title



class hist1():
    def __init__(self, plot_name, plot_title, overlay_list, bin_count, bin_range, **kwargs):
        arg_vals = {
            'normalize': True, 'legend_args':{}, 'xlabel':'', 'ylabel':''
        }
        self.plot_name = plot_name
        self.plot_title = plot_title
        self.data = { label:[] for label in overlay_list }
        self.bins = bin_count
        self.range = bin_range

        arg_vals.update(kwargs)
        for kw,arg in arg_vals.iteritems(): setattr(self, kw, arg)


    def add(self, value, *label):
        if len(label) > 0:
            self.data[label[0]].append(value)
        else
            key0 = list(self.data)[0]
            self.data[key0].append(value)


    def generate_plot():
        plot_values = {'x':[],'weights':[],'label':[]}
        for label, values in self.data.items():
            counts, bins = numpy.histogram(parameter_list, bins=self.bins, range=self.range)
            vals = counts / counts.sum() if self.normalize else counts
            plot_values['x'].append( bins[:-1] )
            plot_values['weights'].append(vals)
            plot_values['label'].append(label)
        plot_values['range'] = self.range
        plot_values['bins'] = self.bins
            
        fig,ax = plt.subplots()
        counts, bins, hist = plt.hist( **plot_values, linewidth=2, histtype='step')

        ax.legend(**self.legend_args)
        plt.grid()
        #plt.yscale('log')
        #plt.ylim(10e-6, 1)
        #plt.ylim(0, 0.2)
        #plt.xlim(0, 2000)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.plot_title)
        fig.savefig('plots/figures/'+self.plot_name+'.pdf')
        plt.close()
