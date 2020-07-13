#!/usr/bin/python3

import numpy
import matplotlib
import random
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle
import itertools
import math
from math import pi

from uproot_methods import TLorentzVector as LV

from uproot_wrapper import event_iterator
import analysis_utils as autils



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
_num_events_to_check = 100

_input_branches = [
    'eventNumber',
    'nresolvedJets',
    ('resolved_jets', [ 'resolvedJets_pt', 'resolvedJets_phi', 'resolvedJets_eta', 'resolvedJets_E', #resolved pt in GeV
        'resolvedJets_HadronConeExclTruthLabelID', 'resolvedJets_is_DL1r_FixedCutBEff_77'
    ])
]

_output_branches = ['event_number']

make_reco_vector = lambda jet: LV.from_ptetaphie(jet['resolvedJets_pt'], jet['resolvedJets_eta'], jet['resolvedJets_phi'], jet['resolvedJets_E'])


def get_vbf_jet_info(non_b_tagged_jets):
    vbf_jet_info = {'x':[], 'y':[], 'c':[]}
    if len(non_b_tagged_jets) > 1:
        mjj_pair = max( [ ( (pair[0]+pair[1]).mass, pair ) for pair in itertools.combinations(non_b_tagged_jets,2) ] )[1]
        color = 'white' if abs(mjj_pair[0].eta - mjj_pair[1].eta) > 3 else 'black'
        vbf_jet_info['x'] = [mjj_pair[0].eta, mjj_pair[1].eta]
        vbf_jet_info['y'] = [mjj_pair[0].phi, mjj_pair[1].phi]
        vbf_jet_info['c'] = [color,color]
    return vbf_jet_info
     


def process_jets(event, ax):
    non_b_tagged_jets = []
    jet_info = {'x':[], 'y':[], 'c':[]}
    for jet in event['resolved_jets']:
        v = make_reco_vector(jet) 
        if v.pt < 30: continue
        jet_info['x'].append(v.eta)
        jet_info['y'].append(v.phi)
        jet_info['c'].append(v.pt)

        # Mark jet circles based on what they are
        color = 'yellow' if abs(jet['resolvedJets_HadronConeExclTruthLabelID']) == 5 else 'blue'
        ax.add_artist( Circle( xy=(v.eta, v.phi), radius=_jet_radius, facecolor='None', edgecolor=color, linewidth=5) )
        if jet['resolvedJets_is_DL1r_FixedCutBEff_77']:
            ax.add_artist( Circle( xy=(v.eta, v.phi), radius=_jet_radius, facecolor='None', edgecolor='red') )
        else:
            non_b_tagged_jets.append(v)

    vbf_jet_info = get_vbf_jet_info(non_b_tagged_jets)
    

    #for key,val in jet_info.items(): print(key, val)
    #for key,val in track_info.items(): print(key, val)
    #print()
    return jet_info, vbf_jet_info



def display_event(event, output, plot_title):
    fig,ax = plt.subplots()
    ax.set_facecolor('0.4') # Make the background grey so you can see the lighter colors
    jet_info, vbf_jet_info = process_jets(event, ax)
    vbf_jet_markers = plt.scatter(**vbf_jet_info, marker='x', s=144)
    jet_scatter = plt.scatter(**jet_info, cmap='plasma', vmin=30, vmax=150, marker='P')

    cbar = plt.colorbar(jet_scatter)
    cbar.set_label('Jet $p_t$ (GeV)')
    plt.axvline(x=2.5)
    plt.axvline(x=-2.5)
    plt.xlim(-5, 5)
    plt.ylim(-pi, pi)
    plt.yticks(ticks=_phiticks, labels=_philabels)
    plt.xlabel('Jet $\eta$')
    plt.ylabel('Jet $\phi$')
    plt.title(plot_title)

    #plt.show()
    output.savefig()
    plt.close()



def display(dataset_key, passes_event_test, type_name, type_title, bgd=True, cvv_value=-1):
    mini_events = event_iterator(autils.input_datasets[dataset_key], 'XhhMiniNtuple', _input_branches, _num_events_to_check)
    nano_events = event_iterator(autils.output_datasets[dataset_key], 'VBF_tree', _output_branches, None)
    nano_event_dictionary = { event['event_number']:None for event in nano_events}

    print( 'Displaying ' + type_name )
    output = PdfPages('figures/event_displays/fig_event_display_'+type_name+'.pdf')
    for event_index, event in enumerate(mini_events):
        if passes_event_test(event):
            plot_title = 'Event Display for ' + type_title + ' #' + str(event_index) 
            display_event(event, output, plot_title)
    output.close()



def pass_all(event):
    return True



def event_display():
    display('MC16d_VBF-HH-bbbb_cvv1', pass_all, 'vbf_all', 'VBF C2V=1', bgd=False, cvv_value=1)
    display('MC16d_ggF-HH-bbbb', pass_all, 'ggF_all', 'ggF')


event_display()

