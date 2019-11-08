#!/usr/bin/env python

import sys
sys.path.append('/nfs/slac/g/atlas/u02/cmilke/analysis/util')
import cmilke_analysis_utils as autils
import math
import pickle

#Define all the high level root stuff: ntuple files, branches to be used
_input_type_options = {
    'sig': autils.Flavntuple_list_VBFH125_gamgam[:1],
    'bgd': autils.Flavntuple_list_ggH125_gamgam[:1]
}

_branch_list = {
    'j0'    : ['tj0pT', 'j0truthid', 'j0_isTightPhoton', 'j0_isPU', 
                        'j0_JVT', 'j0_fJVT_Tight', 'j0pT', 'j0eta', 'j0phi', 'j0m']
}


def record_events(input_type):
    event_categories = {
        '2quarks': 0
      , '3quarks': 0
      , '3withPU': 0
    }

    categories = {
        'all': 0
      , 'PU': 0
      , 'Soft': 0
      , 'passes cJVT': 0
      , 'passes fJVT': 0
      , 'passes JVT': 0
      , 'passes JVT and not PU': 0
      , 'passes JVT and is PU': 0
      , 'fails JVT but is not PU': 0
    }

    input_list = _input_type_options[input_type]
    for event in autils.event_iterator(input_list, 'Nominal', _branch_list, 10000, None):
        num_pu = 0
        num_quarks = 0
        for rj in autils.jet_iterator(_branch_list['j0'], event['j0']):
            if not ( rj['j0pT'] > 30 and abs(rj['j0eta']) < 4 ) or rj['j0_isTightPhoton']: continue
            categories['all'] += 1
            if rj['j0_isPU']:
                categories['PU'] += 1
            if rj['tj0pT'] < 0:
                categories['Soft'] += 1
            if rj['j0_JVT']:
                categories['passes cJVT'] += 1
            if rj['j0_fJVT_Tight']:
                categories['passes fJVT'] += 1
            if rj['j0_JVT'] and rj['j0_fJVT_Tight']:
                categories['passes JVT'] += 1
            if not rj['j0_isPU'] and rj['j0_JVT'] and rj['j0_fJVT_Tight']:
                categories['passes JVT and not PU'] += 1
            if rj['j0_isPU'] and rj['j0_JVT'] and rj['j0_fJVT_Tight']:
                categories['passes JVT and is PU'] += 1
            if not rj['j0_isPU'] and not (rj['j0_JVT'] and rj['j0_fJVT_Tight']):
                categories['fails JVT but is not PU'] += 1

            if rj['tj0pT'] < 0: num_pu += 1
            elif rj['j0truthid'] in autils.PDG['quarks']: num_quarks += 1

            if num_quarks == 2: event_categories['2quarks'] += 1
            if num_quarks == 3: event_categories['3quarks'] += 1
            if num_pu >= 1 and num_quarks == 2: event_categories['3withPU'] += 1


    for key,value in categories.items():
        fraction = value / categories['all']
        print('{}: {}, {:.2}'.format(key,value,fraction))
    print('\n\n')
    for key,value in event_categories.items():
        print('{}: {}'.format(key,value))

record_events('sig')
