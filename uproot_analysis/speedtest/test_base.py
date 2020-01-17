#!/usr/bin/env python
from acorn_backend import analysis_utils as autils
import uproot

input_list = autils.Flavntuple_list_VBFH125_gamgam

_branch_list = [
    'eventWeight',
    'tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm',
    'truthjpT', 'truthjeta', 'truthjphi', 'truthjm',
    'tj0pT', 'j0truthid', 'j0_isTightPhoton', 'j0_isPU', 
    'j0_JVT', 'j0_fJVT_Loose', 'j0_fJVT_Tight', 'j0pT', 'j0eta', 'j0phi', 'j0m'
]

_Nevents = None


def test():
    meaningless_number = 0

    num_events = 0
    for ntuple_file in input_list:
        tree = uproot.rootio.open(ntuple_file)['Nominal']
        tree_iterator = tree.iterate(branches=_branch_list, entrysteps=10000) 
        for basket in tree_iterator:
            for i in range( len(basket[b'eventWeight']) ):
                meaningless_number += basket[b'eventWeight'][i]
                for j in range( len(basket[b'tpartpdgID'][i]) ):
                    meaningless_number += basket[b'tpartpdgID'][i][j]
                    meaningless_number += basket[b'tpartstatus'][i][j]
                    meaningless_number += basket[b'tpartpT'][i][j]
                    meaningless_number += basket[b'tparteta'][i][j]

                for j in range( len(basket[b'j0truthid'][i]) ):
                    meaningless_number += basket[b'j0truthid'][i][j]
                    meaningless_number += basket[b'j0_isTightPhoton'][i][j]
                    meaningless_number += basket[b'j0pT'][i][j]
                    meaningless_number += basket[b'j0eta'][i][j]
                num_events += 1
                if num_events % 10000 == 0: print('Finished ' + str(num_events))
                #if num_events >= _Nevents: break
            #if num_events >= _Nevents: break
        #if num_events >= _Nevents: break

    print(meaningless_number)


test()
