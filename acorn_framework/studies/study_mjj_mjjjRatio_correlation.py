#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

_category_key = 'JVT'
_selector_key = 'mjjmax'
_hist_bins = 20 #(100,100)
_hist_range = ( (0,500), (1,2) )
#_hist_range = ( (0,7), (0,10) )
_bin_skip = slice( None, None, int(_hist_bins/10) )


def retrieve_parameter(input_type):
    parameter_list = ([], [])
    weight_list = []

    data_dump = pickle.load( open('data/output_'+input_type+'.p', 'rb') )
    event_index = 0
    for event in data_dump[_category_key].events:
        #if event_index >= 10: break
        if len(event.jets) != 3: continue
        event_index += 1

        selector = event.selectors[_selector_key]
        mjj = event.selectors[_selector_key].taggers['mjj'].discriminant
        mjjj = event.selectors[_selector_key].taggers['mjjj'].discriminant
        event_weight = event.event_weight
        parameter_list[0].append(mjj)
        parameter_list[1].append(mjjj/mjj)
        weight_list.append(event_weight)
    counts, xedges, yedges = numpy.histogram2d(*parameter_list, weights=weight_list, bins=_hist_bins, range=_hist_range)
    counts = counts.flatten() / counts.sum()
    bins = numpy.array([ (x,y) for x in xedges[:-1] for y in yedges[:-1] ]).transpose()
    return ( counts, bins )


def draw_distribution(input_type):
    print('plotting ' + input_type)
    weights, vals = retrieve_parameter(input_type)

    fig,ax = plt.subplots()
    counts, xbins, ybins, hist = plt.hist2d( *vals,
        weights=weights,
        bins=_hist_bins,
        range=_hist_range)
    cbar = plt.colorbar()
    #plt.clim(0,0.025)

    #plt.grid()
    #plt.yscale('log')
    #plt.ylim(10e-6, 1)
    plt.xlabel('$M_{jj}$ (GeV)')
    plt.ylabel('$M_{jjj}/M_{jj}$')
    plt.xticks(xbins[_bin_skip])
    plt.yticks(ybins[_bin_skip])
    plt.title('')
    fig.savefig('plots/fig_mjj_mjjjRatio_'+input_type+'_correlation.pdf')
    plt.close()


draw_distribution('sig')
#draw_distribution('bgd')
