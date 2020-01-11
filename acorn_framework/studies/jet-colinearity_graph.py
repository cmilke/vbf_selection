#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import sys
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib import rc
rc('text', usetex=True)
from matplotlib.backends.backend_pdf import PdfPages
from acorn_backend.analysis_utils import reload_data

_category_key = 'JVT'

def retrieve_data():
    data_dump = pickle.load( open('data/output_aviv_record_sig.p', 'rb') )
    data_list = []

    event_index = 0
    for event in data_dump[_category_key].events:
        if len(event.jets) != 3: continue
        # Use quark jets as primaries
        primary_jets = []
        for jet in event.jets: 
            if jet.truth_id in range(1,7): primary_jets.append(jet)
            else: extra_jet = jet

        # Use highest pt jets as primaries
        #jets = sorted(event.jets, key = lambda j:j.vector.pt)
        #primary_jets = jets[1:]
        #extra_jet = jets[0]

        if len(primary_jets) != 2: continue
        primary_jets.sort(key=lambda j: j.vector.eta)

        event_index += 1
        #if event_index >= 1000: break

        primary_Deta = primary_jets[1].vector.eta - primary_jets[0].vector.eta
        extra_Deta = extra_jet.vector.eta - primary_jets[0].vector.eta
        data_list.append( (primary_Deta, extra_Deta, extra_jet.vector.pt) )

    print(event_index)
    return data_list


def draw_graph(retrieved_data_values, pt_min, pt_max):
    print('Plotting for: ' + str((pt_min, pt_max)))
    graph_data = [ d for d in retrieved_data_values if pt_min < d[2] and d[2] < pt_max ]
    graph_data.sort( key = lambda d: d[0] ) # Sort by primary Deta

    prim_xpoints = [ prim for prim,extra,pt in graph_data]
    extra_xpoints = [ extra for prim,extra,pt in graph_data]
    ypoints = list( range( len(graph_data) ) )
    cpoints = [pt for q,g,pt in graph_data]

    fig,ax = plt.subplots()
    plt.axvline(x=0, color='black')
    prim_line = plt.plot(prim_xpoints, ypoints, color='black')
    jet_scatter = plt.scatter(extra_xpoints, ypoints, 1, marker='.', c=cpoints, cmap='plasma_r', vmin=30, vmax=100)

    cbar = plt.colorbar(jet_scatter)
    cbar.set_label('Gluon Jet $p_T$ (GeV)')

    #ax.legend(loc='upper center')
    #ax.legend()
    #plt.grid()
    #plt.yscale('log')
    plt.xlim(-10,10)
    #plt.ylim(2,)
    plt.xlabel(r'$\Delta \eta _ {gluon}$')
    plt.ylabel('Event Number, Sorted by $\Delta \eta_{quarks}$')
    plt.title('Gluon $\Delta \eta$ Distribution\n For Gluon Jets with $'+str(pt_min)+'< p_T <'+str(pt_max)+'$ GeV (Total = '+str(len(graph_data))+' Jets)')
    fig.savefig('plots/figures/jet-colinearity_graph_'+str(pt_min)+'-'+str(pt_max)+'.pdf')
    plt.close()


def draw_normalized_graph(retrieved_data_values, pt_min, pt_max):
    print('Plotting for: ' + str((pt_min, pt_max)))
    graph_data = [ d for d in retrieved_data_values if pt_min < d[2] and d[2] < pt_max ]
    graph_data.sort( key = lambda d: d[0] ) # Sort by primary Deta

    fig,ax = plt.subplots()
    plt.axvline(x=1, color='black')
    xpoints = [abs(extra/prim-.5)*2 for prim,extra,pt in graph_data]
    ypoints = [prim for prim,extra,pt in graph_data]
    cpoints = [pt for q,g,pt in graph_data]
    jet_scatter = plt.scatter(xpoints, ypoints, 1, marker='.', c=cpoints, cmap='plasma_r', vmin=30, vmax=100)

    cbar = plt.colorbar(jet_scatter)
    cbar.set_label('Gluon Jet $p_T$ (GeV)')

    #ax.legend(loc='upper center')
    #ax.legend()
    #plt.grid()
    #plt.yscale('log')
    plt.xlim(0,3)
    plt.ylim(2,)
    plt.xlabel(r'$ 2 \times | \frac{\eta_g - \eta_L}{\eta_R - \eta_L} - 0.5 | $')
    plt.ylabel(r'$\eta_R - \eta_L$')
    plt.title('Normalized Gluon $\Delta \eta$ Distribution\n For Gluon Jets with $'+str(pt_min)+'< p_T <'+str(pt_max)+'$ GeV (Total: '+str(len(graph_data))+' Jets)')
    fig.savefig('plots/figures/jet-colinearity_graph_normalized'+str(pt_min)+'-'+str(pt_max)+'.pdf')
    plt.close()


def draw_2dhist(retrieved_data_values, pt_min, pt_max):
    print('Plotting for: ' + str((pt_min, pt_max)))
    graph_data = [ d for d in retrieved_data_values if pt_min < d[2] and d[2] < pt_max ]
    graph_data.sort( key = lambda d: d[0] ) # Sort by primary Deta

    xinputs = [abs(extra/prim-.5)*2 for prim,extra,pt in graph_data]
    yinputs = [pt for q,g,pt in graph_data]
    hist_range = ( (0,2), (pt_min,pt_max) )
    hist_bins = 50
    counts, xedges, yedges = numpy.histogram2d( xinputs, yinputs, bins=hist_bins, range=hist_range )
    counts = (counts / counts.sum(0)).flatten()
    hist_edges = numpy.array([ (x,y) for x in xedges[:-1] for y in yedges[:-1] ]).transpose()

    fig,ax = plt.subplots()
    plt.axvline(x=1, color='red')
    counts, xbins, ybins, hist = plt.hist2d( *hist_edges, weights=counts, bins=hist_bins, range=hist_range)
    cbar = plt.colorbar()
    
    #plt.grid()
    #plt.yscale('log')
    #plt.xlim(0,3)
    #plt.ylim(pt_min, pt_max)
    plt.xlabel(r'$ 2 \times | \frac{\eta_g - \eta_L}{\eta_R - \eta_L} - 0.5 | $')
    plt.ylabel(r'gluon $p_T$ (GeV)')
    cbar.set_label(r'Fraction of Events \textit{In Same $p_T$ Bin}')
    plt.title('')
    fig.savefig('plots/figures/jet-colinearity_2dhist'+str(pt_min)+'-'+str(pt_max)+'.pdf')
    plt.close()


def draw_all():
    retrieved_data_values = reload_data(len(sys.argv) > 1, retrieve_data)

    #draw_normalized_graph(retrieved_data_values,30,200)
    #draw_normalized_graph(retrieved_data_values,30,60)
    #draw_normalized_graph(retrieved_data_values,60,200)

    #draw_graph(retrieved_data_values,30,200)
    #draw_graph(retrieved_data_values,30,60)
    #draw_graph(retrieved_data_values,60,200)

    draw_2dhist(retrieved_data_values,30,100)
    draw_2dhist(retrieved_data_values,30,200)
    draw_2dhist(retrieved_data_values,30,60)


draw_all()
