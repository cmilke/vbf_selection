import pickle

import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

Hist_bins = 200

_discriminant_ranges = {
    'mjj': (0,3000),
    'Deta': (0,10),
    'centrality': (0,100),
    'Fcentrality': (0,1)
}

_tagger_idents = {
    'mjj': 'mjj',
    'mjN': 'mjj',
    'mjj_from_leading_pt': 'mjj',
    'mjjmax': 'mjj',
    'mjjSL': 'mjj',
    'mjj_of_random_jets': 'mjj',
}


# Used by the retrieve_data function to deal with the intricacies of 
# dumping valies into the data map
def fill_event_map(event_map, event_key, discriminant, event_weight):
    tagger_key = event_key[-1]
    value_range = _discriminant_ranges[ _tagger_idents[tagger_key] ]

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
            for tagger_key, discriminant in event.discriminants.items():
                event_key = (jet_count, category.key, tagger_key)
                fill_event_map(event_map, event_key, discriminant, event_weight)
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
    title = num_title+category_title+' : ' + event_key[2]
    return title


class hist1():
    def __init__(self, plot_name, plot_title, overlay_list, bin_count, bin_range, **kwargs):
        arg_vals = { 
            'normalize': True, 'legend_args':{}, 'xlabel':'', 'ylabel':'',
            'xlim':None, 'ylim':None
        }
        self.plot_name = plot_name
        self.plot_title = plot_title
        self.data = { label:[] for label in overlay_list }
        self.bins = bin_count
        self.range = bin_range

        arg_vals.update(kwargs)
        for kw,arg in arg_vals.items(): setattr(self, kw, arg)


    def add(self, value, *label):
        if len(label) > 0:
            self.data[label[0]].append(value)
        else:
            key0 = list(self.data)[0]
            self.data[key0].append(value)


    def generate_plot(self, refresh, cache):
        print('Plotting '+self.plot_name)
        if refresh: cache[self.plot_name] = self.data
        else: self.data = cache[self.plot_name]

        plot_values = {'x':[],'weights':[],'label':[]}
        for label, values in self.data.items():
            counts, bins = numpy.histogram(values, bins=self.bins, range=self.range)
            if counts.sum() == 0: 
                print('WARNING: '+self.plot_name + ' has no data for label ' + label)
                if len(values) == 0:
                    print('Label list is empty')
                else:
                    print( 'Label list contains {} values between {} and {}'.format(len(values), min(values), max(values)) )
                return
            binned_vals = counts / counts.sum() if self.normalize else counts
            plot_values['x'].append( bins[:-1] )
            plot_values['weights'].append(binned_vals)
            plot_values['label'].append(label)
        plot_values['range'] = self.range
        plot_values['bins'] = self.bins
            
        fig,ax = plt.subplots()
        counts, bins, hist = plt.hist( **plot_values, linewidth=2, histtype='step')

        if len(plot_values['label']) > 1: ax.legend(**self.legend_args)
        plt.grid()
        #plt.yscale('log')
        if self.xlim != None: plt.xlim(*self.xlim)
        if self.ylim != None: plt.ylim(*self.ylim)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.plot_title)
        fig.savefig('plots/figures/'+self.plot_name+'.pdf')
        plt.close()



class hist2():
    def __init__(self, plot_name, plot_title, bin_count, bin_range, **kwargs):
        arg_vals = { 'normalize': True, 'xlabel':'', 'ylabel':'', 'zlim':None }
        self.plot_name = plot_name
        self.plot_title = plot_title
        self.data = ([],[])
        self.bins = bin_count
        self.range = bin_range

        arg_vals.update(kwargs)
        for kw,arg in arg_vals.items(): setattr(self, kw, arg)


    def add(self, value0, value1):
        self.data[0].append(value0)
        self.data[1].append(value1)


    def generate_plot(self, refresh, cache):
        print('Plotting '+self.plot_name)
        if refresh: cache[self.plot_name] = self.data
        else: self.data = cache[self.plot_name]

        hist_counts, xedges, yedges = numpy.histogram2d(*self.data, bins=self.bins, range=self.range)
        flat_counts = hist_counts.flatten()
        if flat_counts.sum() == 0: 
            print('WARNING: '+self.plot_name + ' has no data')
            print(*self.data)
            return
        if self.normalize: flat_counts /= hist_counts.sum()
        bin_edges = numpy.array([ (x,y) for x in xedges[:-1] for y in yedges[:-1] ]).transpose()

        fig,ax = plt.subplots()
        counts, xbins, ybins, hist = plt.hist2d( *bin_edges, weights=flat_counts, bins=self.bins, range=self.range)

        cbar = plt.colorbar()
        if self.zlim != None: plt.clim(self.zlim)

        #plt.grid()
        #plt.yscale('log')
        #plt.ylim(10e-6, 1)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.plot_title)
        fig.savefig('plots/figures/'+self.plot_name+'.pdf')
        plt.close()
