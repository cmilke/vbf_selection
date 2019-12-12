#!/usr/bin/env python

from acorn_backend import acorn_utils as autils
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

def tally_events(input_type):
    print('INPUT: ' + input_type)
    input_list = _input_type_options[input_type]
    for event in autils.event_iterator(input_list, 'Nominal', _branch_list, 100, 0):
        for tp in autils.jet_iterator(event['tpart']):
            pdgid = tp['tpartpdgID']
            status = tp['tpartstatus']
            if (pdgid == autils.PDG['photon']): print(pdgid, status)
            #if (status == 62): print(pdgid, status)
            #if ((status == 44 or status == 62) and pdgid != 25): print(pdgid, status)
            #if (pdgid in autils.PDG['quarks'] or pdgid == 21) and status != 23: print(pdgid, status)
            #if pdgid == 21 and status != 23: print(pdgid, status)


tally_events('sig')
#tally_events('bgd')
