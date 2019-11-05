#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle
from math import pi
from acorn_backend import jet_selectors


_phiticks=[ -4, -(4/4)*pi,-(3/4)*pi, -(2/4)*pi, -(1/4)*pi, 0, (1/4)*pi, (2/4)*pi, (3/4)*pi, (4/4)*pi , 4]
_philabels=[
    r''
  , r'$-\pi$'
  , r'$-\frac{3}{4}\pi$'
  , r'$-\frac{1}{2}\pi$'
  , r'$-\frac{1}{4}\pi$'
  , r'$0$'
  , r'$\frac{1}{4}\pi$'
  , r'$\frac{1}{2}\pi$'
  , r'$\frac{3}{4}\pi$'
  , r'$\pi$'
  , r''
]
_jet_radius=0.4


def display_events(event_type, type_name):
    print( 'Displaying ' + type_name )
    output = PdfPages('plots/fig_event_display_'+type_name+'.pdf')
    for jets in event_type:
        fig,ax = plt.subplots()
        ax.set_facecolor('0.4')
        jet_scatter = plt.scatter(jets[1], jets[2], c=jets[3], cmap='plasma', vmin=0, vmax=100)
        for x,y,z,c in zip(*jets[1:]):
            ax.add_artist( Circle( xy=(x, y), radius=_jet_radius, facecolor='None', edgecolor=c) )

        cbar = plt.colorbar(jet_scatter)
        cbar.set_label('Jet $p_t$ (GeV)')
        plt.xlim(-5, 5)
        plt.ylim(-pi, pi)
        plt.yticks(ticks=_phiticks, labels=_philabels)
        plt.xlabel('Jet $\eta$')
        plt.ylabel('Jet $\phi$')

        plt.title( 'Event Display for Event ' + str(jets[0]) )
        #plt.show()
        output.savefig()
        plt.close()
    output.close()


def display():
    category_key = 'JVT'
    selector_key = 'etamax'
    tagger_key = 'mjjj'
    tagger_cut = 500 # GeV

    all_events = []
    correctly_selected_events = []
    misselected_events = []

    data_dump = pickle.load( open('data/output_sig.p', 'rb') )
    event_index = 0
    for event in data_dump[category_key].events:
        if event_index >= 100: break
        if len(event.jets) != 3: continue
        event_index += 1

        selector = event.selectors[selector_key]
        tagger = selector.taggers[tagger_key]
        info = [ event_index, [], [], [], [] ] #eta, phi, pt
        for jet in event.jets:
            info[1].append(jet.eta)
            info[2].append(jet.phi)
            info[3].append(jet.pt)
            color = 'blue'
            if jet.is_truth_quark(): color = 'yellow'
            info[4].append(color)
        all_events.append(info)
        #if selector.is_correct: correctly_selected_events.append(info)
        if tagger.discriminant > tagger_cut: correctly_selected_events.append(info)
        else: misselected_events.append(info)



    display_events( all_events, 'all' )
    display_events( correctly_selected_events, 'correct' )
    display_events( misselected_events, 'wrong' )

display()
