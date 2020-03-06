#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import pickle
import numpy
import matplotlib
import random
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle
import math
from math import pi

from acorn_backend.tagger_methods import tagger_options


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
_category_key = 'JVT'
_num_events_to_check = 100
_display_pull = True
_display_tracks = False
_mjjj_80percent_rejection_cut = 630 # GeV
_mjj_2maxpt_80percent_rejection_cut = 400 # GeV
_mjj_mjjmax_80percent_rejection_cut = 500 # GeV
#_mjj_2maxpt_40percent_rejection_cut = 170 # GeV , for all
#_mjj_mjjmax_40percent_rejection_cut = 210 # GeV , for all
_mjj_2maxpt_40percent_rejection_cut = 778 # GeV , for mjj > 500
_mjj_mjjmax_40percent_rejection_cut = 812 # GeV , for mjj > 500

#_jet_marker_style = matplotlib.markers.MarkerStyle(marker='o', fillstyle='none')


# This is only for testing purposes
def make_random_tracks(track_info, jet_vector):
    num_tracks = random.randint(1,4)
    for track_index in range(num_tracks):
        track_radius = random.randint(0,400)/1000
        track_angle = 2*pi * random.randint(0,99)/100
        eta = track_radius * math.cos(track_angle) + jet_vector.eta
        phi = track_radius * math.sin(track_angle) + jet_vector.phi
        pt = (jet_vector.pt / num_tracks) * random.gauss(1, 0.2)
        track_info['x'].append(eta)
        track_info['y'].append(phi)
        track_info['c'].append(pt)


def process_jets(event, ax):
    jet_info = {'x':[], 'y':[], 'c':[]}
    track_info = {'x':[], 'y':[], 'c':[]}
    for jet in event.jets:
        jet_info['x'].append(jet.eta())
        jet_info['y'].append(jet.phi())
        jet_info['c'].append(jet.pt())

        # Mark jet circles based on whether or not the jet is a quark jet
        color = 'yellow' if jet.is_truth_quark() else 'blue'
        ax.add_artist( Circle( xy=(jet.eta(), jet.phi()), radius=_jet_radius, facecolor='None', edgecolor=color) )

        if _display_pull:
            #pull_magnitude = random.randint(0,100)/100
            #pull_angle = 2*pi * random.randint(0,99)/100
            #pull_magnitude = 0.5
            #pull_angle = (2*pi) * (7/8)
            if jet.jet_pull_mag() != -999000.0:
                arrow_dx = 100 * jet.jet_pull_mag() * math.cos(jet.jet_pull_angle())
                arrow_dy = 100 * jet.jet_pull_mag() * math.sin(jet.jet_pull_angle())
                plt.arrow(jet.eta(), jet.phi(), arrow_dx, arrow_dy, width=0.03, zorder=10)

        if _display_tracks:
            #make_random_tracks(track_info, v)
            for track in jet.tracks:
                track_info['x'].append(track.vector.eta)
                track_info['y'].append(track.vector.phi)
                track_info['c'].append(track.vector.pt)

    #for key,val in jet_info.items(): print(key, val)
    #for key,val in track_info.items(): print(key, val)
    #print()
    return jet_info, track_info


def display_event(event, output, plot_title):
    fig,ax = plt.subplots()
    ax.set_facecolor('0.4') # Make the background grey so you can see the lighter colors
    jet_info, track_info = process_jets(event, ax)
    jet_scatter = plt.scatter(**jet_info, cmap='plasma', vmin=0, vmax=100, marker='P')
    track_scatter = plt.scatter(**track_info, cmap='plasma', vmin=0, vmax=100, marker='2')

    cbar = plt.colorbar(jet_scatter)
    cbar.set_label('Jet/Track $p_t$ (GeV)')
    plt.xlim(-5, 5)
    plt.ylim(-pi, pi)
    plt.yticks(ticks=_phiticks, labels=_philabels)
    plt.xlabel('Jet $\eta$')
    plt.ylabel('Jet $\phi$')
    plt.title(plot_title)

    #plt.show()
    output.savefig()
    plt.close()


def display(event_list, passes_event_test, type_name, type_title):
    print( 'Displaying ' + type_name )
    output = PdfPages('plots/event_displays/fig_event_display_'+type_name+'.pdf')
    for event_index, event in enumerate(event_list):
        if passes_event_test(event):
            plot_title = 'Event Display for ' + type_title + ' ' + str(event_index) 
            display_event(event, output, plot_title)
    output.close()


def pass_all(event):
    return True


def passes_mjjj(event):
    mjjj = tagger_options['>=3jet']['mjN'](event)
    return mjjj > _mjjj_80percent_rejection_cut 
    

def fails_mjjj(event):
    return not passes_mjjj(event)



def event_display():
    #sig_data_dump = pickle.load( open('data/output_aviv_tag_sig.p', 'rb') )
    sig_data_dump = pickle.load( open('data/output_cmilke_record_sig.p', 'rb') )
    sig_event_list = [ event for event in sig_data_dump[_category_key].events if len(event.jets) > 2 ][:_num_events_to_check]
    #sig_event_list = [ event for event in sig_data_dump[_category_key].events if len(event.jets) == 2 ][:_num_events_to_check]

    #bgd_data_dump = pickle.load( open('data/output_aviv_tag_bgd.p', 'rb') )
    #bgd_event_list = [ event for event in bgd_data_dump[_category_key].events if len(event.jets) > 2 ][:_num_events_to_check]

    display(sig_event_list, pass_all, 'all', 'Signal Event')


event_display()
