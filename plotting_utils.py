import pickle

import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt


_output_dir = 'figures/'
#_output_ext = '.png'
_output_ext = '.pdf'


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
                print('WARNING: '+self.plot_name + ' has no data for label ' + str(label))
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
        fig.savefig(_output_dir+self.plot_name+_output_ext)
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
        fig.savefig(_output_dir+self.plot_name+_output_ext)
        plt.close()



class roc():
    def __init__(self, plot_name, plot_title, overlay_list, **kwargs):
        arg_vals = { 
            'legend_args':{}, 'labelmaker':None, 'normalize': True, 'scale_to_y': False,
            'zooms': []
        }
        self.plot_name = plot_name
        self.plot_title = plot_title
        self.data = { label:([],[]) for label in overlay_list }
        self.marker_requests = { label:[] for label in overlay_list }

        arg_vals.update(kwargs)
        for kw,arg in arg_vals.items(): setattr(self, kw, arg)


    def add_marker(self, label, marker_value, **kwargs):
        if 'annotation' not in kwargs: kwargs['annotation'] = ''
        self.marker_requests[label].append( (marker_value, kwargs) )


    def fill(self, value, bgd, *label, weight=1):
        key = list(self.data)[0] if len(label) == 0 else label[0]
        self.data[key][bgd].append( (value,weight) )


    def generate_plot(self, refresh, cache):
        print('Plotting '+self.plot_name)
        if refresh: cache[self.plot_name] = self.data
        else: self.data = cache[self.plot_name]

        roc_ax = plt.subplots()
        set_markers = []
        for label, (signal,background) in self.data.items():
            pending_markers = self.marker_requests[label]
            pending_markers.sort(reverse=True) # This way I can use "pop"

            signal = numpy.array(signal)
            background = numpy.array(background)
            signal = signal[ signal[:,0].argsort() ]
            background = background[ background[:,0].argsort() ]
            total_signal = signal.sum(axis=0)[1]
            total_background = background.sum(axis=0)[1]

            efficiency_list = []
            rejection_list = []
            #efficiency_list = [total_signal]
            #rejection_list = [0]
            #if self.normalize: efficiency_list[0] = 1
            bgd_index = 0
            summed_rejection = 0
            summed_efficiency = total_signal
            for sig_val, sig_weight in signal:
                summed_efficiency -= sig_weight
                while bgd_index < len(background) and background[bgd_index][0] < sig_val:
                    summed_rejection += background[bgd_index][1]
                    bgd_index+=1

                efficiency = summed_efficiency
                rejection = summed_rejection
                if self.normalize:
                    efficiency /= total_signal
                    rejection /= total_background

                efficiency_list.append(efficiency)
                rejection_list.append(rejection)
                if len(pending_markers) != 0 and sig_val > pending_markers[-1][0]:
                    location = (efficiency, rejection)
                    kwargs = pending_markers.pop()[1]
                    set_markers.append( (location, kwargs) )

            plt.plot(efficiency_list, rejection_list, label=label, linewidth=1)
        plt.legend(prop={'size':6})
        plt.xlabel('Signal Efficiency')
        plt.ylabel('Background Rejection')
        plt.title(self.plot_title)
        plt.grid(True)
        for location, kwargs in set_markers:
            annotation_text = kwargs.pop('annotation')
            plt.annotate(annotation_text, xy=location, fontsize='x-small')
            plt.plot(*location, **kwargs)

        plt.savefig(_output_dir+self.plot_name+_output_ext)
        for index, (xlim, ylim) in enumerate(self.zooms):
            plt.xlim(*xlim)
            plt.ylim(*ylim)
            plt.savefig(_output_dir+self.plot_name+f'_zoom{index}'+_output_ext)
        plt.close()



class plot_wrapper():
    def __init__(self, blacklist):
        self.plot_dict = {}
        self.blacklist = blacklist

    def add_hist1(self, plot_name, *args, **kwargs):
        self.plot_dict[plot_name] = hist1(plot_name, *args, **kwargs)

    def add_hist2(self, plot_name, *args, **kwargs):
        self.plot_dict[plot_name] = hist2(plot_name, *args, **kwargs)

    def add_roc(self, plot_name, *args, **kwargs):
        self.plot_dict[plot_name] = roc(plot_name, *args, **kwargs)

    #def add_roc_group(self, plot_name, *args, **kwargs):
    #    self.plot_dict[plot_name] = roc(plot_name, *args, **kwargs)
    #    self.plot_dict[plot_name+'_Yscaled'] = roc(plot_name, *args, scale_to_y=True, **kwargs)
    #    self.plot_dict[plot_name+'_bare'] = roc(plot_name, *args, normalize=False, **kwargs)

    def plot_all(self, refresh, cache):
        for key,plot in self.plot_dict.items():
            blacklisted = False
            for substring in self.blacklist:
                if substring in key:
                    blacklisted = True
                    break
            if not blacklisted: plot.generate_plot(refresh, cache)

    def __getitem__(self, plot_name):
        return self.plot_dict[plot_name]

