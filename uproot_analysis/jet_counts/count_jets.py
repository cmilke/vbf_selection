#!/usr/bin/env python

from acorn_backend import acorn_utils as autils
from uproot_methods import TLorentzVector
import pickle
import math
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

#Define all the high level root stuff: ntuple files, branches to be used
_input_type_options = {
    'sig': autils.Flavntuple_list_VBFH125_gamgam[:1],
    'bgd': autils.Flavntuple_list_ggH125_gamgam[:1]
}

_branch_list = {
    'event' : ['eventWeight']
  , 'tpart' : ['tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm']
  , 'truthj': ['truthjpT', 'truthjeta', 'truthjphi', 'truthjm']
  , 'j0'    : ['tj0pT', 'j0truthid', 'j0_isTightPhoton', 'j0_isPU', 
                        'j0_JVT', 'j0_fJVT_Loose', 'j0_fJVT_Tight', 'j0pT', 'j0eta', 'j0phi', 'j0m']
}

_pt_cut = 30


def match_jet(vector_to_match, event):
    for tp in autils.jet_iterator(event['tpart']):
        if tp['tpartpdgID'] == autils.PDG['photon']:
            if tp['tpartstatus'] != autils.Status['photon_out']: continue
        elif tp['tpartstatus'] != autils.Status['outgoing']: continue

        truth_vec = TLorentzVector.from_ptetaphim(tp['tpartpT'], tp['tparteta'], tp['tpartphi'], tp['tpartm'])

        deltaR = vector_to_match.delta_r(truth_vec)
        if deltaR < 0.3: return tp['tpartpdgID']
    return -1


def event_fails_photon_cut(event):
    photon_pts = []
    photon_4vector = TLorentzVector.from_ptetaphim(0,0,0,0)
    for tp in autils.jet_iterator(event['tpart']):
        if tp['tpartpdgID'] != autils.PDG['photon']: continue
        if tp['tpartstatus'] != autils.Status['photon_out']: continue
        photon_pts.append(tp['tpartpT'])
        v = TLorentzVector.from_ptetaphim(tp['tpartpT'], tp['tparteta'], tp['tpartphi'], tp['tpartm'])
        photon_4vector += v
    if len(photon_pts) != 2: return True
    mgg = photon_4vector.mass
    photon_pts.sort(reverse=True)
    if photon_pts[0] < 0.35*mgg or photon_pts[1] < 0.25*mgg: return True

    return False


def count_tjets_with_truthj(event):
    num_tjets = 0
    num_tquarks = 0
    for tj in autils.jet_iterator(event['truthj']):
        v = TLorentzVector.from_ptetaphim(tj['truthjpT'], tj['truthjeta'], tj['truthjphi'], tj['truthjm'])
        pdg = match_jet(v, event)
        if pdg == autils.PDG['photon']: continue
        if pdg < 0: continue
        if tj['truthjpT'] < _pt_cut: continue

        num_tjets += 1
        if pdg in autils.PDG['quarks']: num_tquarks += 1
    return num_tjets, num_tquarks
    #return 0,0


def count_rjets(event):
    num_rjets = 0
    num_rquarks = 0
    for rj in autils.jet_iterator(event['j0']):
        v = TLorentzVector.from_ptetaphim(rj['j0pT'], rj['j0eta'], rj['j0phi'], rj['j0m'])
        pdg = match_jet(v, event)

        if pdg == autils.PDG['photon']: continue
        #if rj['j0_isTightPhoton']: continue
        if rj['j0pT'] < _pt_cut: continue
        if not (rj['j0_JVT'] and rj['j0_fJVT_Tight']): continue

        num_rjets += 1
        if pdg in autils.PDG['quarks']: num_rquarks += 1
    return num_rjets, num_rquarks
    #return 3,3


def count_all_jets(input_type):
    tcounter = []
    rcounter = []

    input_list = _input_type_options[input_type]
    for event in autils.event_iterator(input_list, 'Nominal', _branch_list, 10000, 0):
        if event_fails_photon_cut(event): continue
        num_tjets, num_tquarks = count_tjets_with_truthj(event)
        num_rjets, num_rquarks = count_rjets(event)

        if num_rjets >= 2:
            tcounter.append(num_tjets)
            rcounter.append(num_rjets)

    return tcounter, rcounter


def tally_events(input_type):
    print('INPUT: ' + input_type)
    tcounter, rcounter = count_all_jets(input_type)
    #for t,r in zip(tcounter,rcounter): print(t,r)

    hist_bins = range(6) 
    display_bins = 10
    counts, xedges, yedges = numpy.histogram2d(tcounter, rcounter, bins=hist_bins)
    counts = counts / counts.sum()
    binned_data = [ (i,j,counts[i][j]) for i in xedges[:-1] for j in yedges[:-1] ]
    binned_data.sort(key=lambda x: x[2], reverse=True)
    for count in binned_data[:display_bins]: print( '({}, {}): {:.2}'.format(*count) )

    plot_data = { 'x': [] , 'weights': [] }
    xlabels = []
    for bin_number, (truth_jets, reco_jets, counts) in enumerate(binned_data[:display_bins]):
        plot_data['x'].append(bin_number)
        plot_data['weights'].append(counts)
        xlabels.append( '({},{})'.format(truth_jets, reco_jets) )

    fig,ax = plt.subplots()
    counts, bins, hist = plt.hist( **plot_data, bins=range(0,display_bins) )
    plt.xticks(ticks=(bins+0.5), labels=xlabels)
    plt.xlabel('(n truth, n reco)')
    plt.ylabel('Fraction')
    plt.ylim(0, 1.0)
    plt.title('VBF truth-reco cases (pT threshold '+str(_pt_cut)+' GeV)')
    fig.savefig('jet_counts_'+str(_pt_cut)+'GeV.pdf')


tally_events('sig')
#tally_events('bgd')
