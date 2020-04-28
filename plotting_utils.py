import pickle

import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt


_output_dir = 'figures/'


class hist1():
    def __init__(self, plot_name, plot_title, overlay_list, bin_count, bin_range, **kwargs):
        arg_vals = { 
            'normalize': True, 'legend_args':{}, 'xlabel':'', 'ylabel':'',
            'xlim':None, 'ylim':None, 'ylog':False, 'labelmaker':None
        }
        self.plot_name = plot_name
        self.plot_title = plot_title
        self.data = { label:[] for label in overlay_list }
        self.bins = bin_count
        self.range = bin_range

        arg_vals.update(kwargs)
        for kw,arg in arg_vals.items(): setattr(self, kw, arg)


    def fill(self, value, *label):
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
            label_text = label if self.labelmaker == None else self.labelmaker(label)
            plot_values['label'].append(label_text)
        plot_values['range'] = self.range
        plot_values['bins'] = self.bins
            
        fig,ax = plt.subplots()
        counts, bins, hist = plt.hist( **plot_values, linewidth=2, histtype='step')

        if len(plot_values['label']) > 1: ax.legend(**self.legend_args)
        plt.grid()
        if self.ylog: plt.yscale('log')
        if self.xlim != None: plt.xlim(*self.xlim)
        if self.ylim != None: plt.ylim(*self.ylim)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.plot_title)
        fig.savefig(_output_dir+self.plot_name+'.png')
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


    def fill(self, value0, value1):
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
        fig.savefig(_output_dir+self.plot_name+'.png')
        plt.close()



class plot_wrapper():
    def __init__(self, blacklist):
        self.plot_dict = {}
        self.blacklist = blacklist

    def add_hist1(self, plot_name, *args, **kwargs):
        self.plot_dict[plot_name] = hist1(plot_name, *args, **kwargs)

    def add_hist2(self, plot_name, *args, **kwargs):
        self.plot_dict[plot_name] = hist2(plot_name, *args, **kwargs)

    def plot_all(self, refresh, cache):
        for key,plot in self.plot_dict.items():
            for substring in self.blacklist:
                if substring in key: continue
            plot.generate_plot(refresh, cache)

    def __getitem__(self, plot_name):
        return self.plot_dict[plot_name]
