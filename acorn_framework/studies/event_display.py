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
_spread = None # I don't think this works correctly...
_category_key = 'JVT'
_num_events_to_check = 20
_display_pull = True
_display_tracks = True
_mjjj_80percent_rejection_cut = 630 # GeV
_mjj_2maxpt_80percent_rejection_cut = 400 # GeV
_mjj_mjjmax_80percent_rejection_cut = 500 # GeV
_mjj_2maxpt_40percent_rejection_cut = 170 # GeV
_mjj_mjjmax_40percent_rejection_cut = 210 # GeV

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
        v = jet.vector
        jet_info['x'].append(v.eta)
        jet_info['y'].append(v.phi)
        jet_info['c'].append(v.pt)

        # Mark jet circles based on whether or not the jet is a quark jet
        color = 'yellow' if jet.is_truth_quark() else 'blue'
        ax.add_artist( Circle( xy=(v.eta, v.phi), radius=_jet_radius, facecolor='None', edgecolor=color) )

        if _display_pull:
            #pull_magnitude = random.randint(0,100)/100
            #pull_angle = 2*pi * random.randint(0,99)/100
            #pull_magnitude = 0.5
            #pull_angle = (2*pi) * (7/8)
            pull_magnitude, pull_angle = jet.pull
            if pull_magnitude != -999000.0:
                arrow_dx = 100 * pull_magnitude * math.cos(pull_angle)
                arrow_dy = 100 * pull_magnitude * math.sin(pull_angle)
                plt.arrow(v.eta, v.phi, arrow_dx, arrow_dy, width=0.03, zorder=10)

        if _display_tracks:
            #make_random_tracks(track_info, v)
            for track in jet.tracks:
                track_info['x'].append(track.vector.eta)
                track_info['y'].append(track.vector.phi)
                track_info['c'].append(track.vector.pt)
            #if (_spread != None):
            #    spread_values = lambda values, jet_v: [ _spread*v - (_spread-1)*jet_v for v in values ]
            #    track_info['x'] = spread_values(track_info['x'], v.eta)
            #    track_info['y'] = spread_values(track_info['y'], v.phi)

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
    num_pass = 0
    for event_index, event in enumerate(event_list):
        if passes_event_test(event):
            num_pass+=1
            plot_title = 'Event Display for ' + type_title + ' ' + str(event_index) 
            display_event(event, output, plot_title)
    output.close()
    print(event_index+1, num_pass, int(100*num_pass/(event_index+1) ) )


def pass_all(event):
    return True


def passes_mjjj(event):
    mjjj = event.selectors['2maxpt'].taggers['mjjj'].discriminant
    return mjjj > _mjjj_80percent_rejection_cut 
    

def fails_mjjj(event):
    return not passes_mjjj(event)


def passes_mjjj_and_fails_mjj2maxpt(event):
    mjjj = event.selectors['2maxpt'].taggers['mjjj'].discriminant
    mjj = event.selectors['2maxpt'].taggers['mjj'].discriminant
    passes_mjjj = mjjj > _mjjj_80percent_rejection_cut 
    fails_mjj = mjj < _mjj_2maxpt_80percent_rejection_cut
    return passes_mjjj and fails_mjj


def tagger_selector_performance_is_inverted(event):
    mjjmax = event.selectors['mjjmax']
    maxpt = event.selectors['2maxpt']

    mjj_from_pt = maxpt.taggers['mjj'].discriminant
    mjj_from_mjj = mjjmax.taggers['mjj'].discriminant
    pt_passes = mjj_from_pt > _mjj_2maxpt_40percent_rejection_cut
    mjj_passes = mjj_from_mjj > _mjj_mjjmax_40percent_rejection_cut

    if maxpt.is_correct and not mjjmax.is_correct:
        if not pt_passes and mjj_passes: return True

    return False


def event_display():
    #sig_data_dump = pickle.load( open('data/output_aviv_tag_sig.p', 'rb') )
    sig_data_dump = pickle.load( open('data/output_cmilke_record_sig.p', 'rb') )
    #sig_event_list = [ event for event in sig_data_dump[_category_key].events if len(event.jets) > 2 ][:_num_events_to_check]
    sig_event_list = [ event for event in sig_data_dump[_category_key].events if len(event.jets) == 2 ][:_num_events_to_check]

    #bgd_data_dump = pickle.load( open('data/output_aviv_tag_bgd.p', 'rb') )
    #bgd_event_list = [ event for event in bgd_data_dump[_category_key].events if len(event.jets) > 2 ][:_num_events_to_check]

    display(sig_event_list, pass_all, 'all', 'Signal Event')
    #display(sig_event_list, tagger_selector_performance_is_inverted, 'inversion', 'Signal Event with Inverted Performance')
    #display(bgd_event_list, tagger_selector_performance_is_inverted, 'inversion', 'Background Event with Inverted Selector/Tagger Performance')

    #display(sig_data_dump, passes_mjjj, 'sig_pass_mjjj', 'Signal Event which\nCorrectly Pass $M_{jjj}$')
    #display(bgd_data_dump, fails_mjjj, 'bgd_fail_mjjj', 'Background Event which\nCorrectly Fail $M_{jjj}$')
    #display(bgd_data_dump, passes_mjjj_and_fails_mjj2maxpt, 'bgd_pass_mjjj_fail_mjj', 'Background Events\nwhich Correctly Fail $M_{jj}$ but Incorrectly Pass $M_{jjj}$')


event_display()
