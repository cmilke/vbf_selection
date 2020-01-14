#!/usr/bin/env python

from acorn_backend import analysis_utils as autils
from acorn_backend.uproot_wrapper import event_iterator
import uproot
from uproot_methods import TLorentzVector

#Define all the high level root stuff: ntuple files, branches to be used
_input_type_options = {
    'sig': autils.Flavntuple_list_VBFH125_gamgam,
    'bgd': autils.Flavntuple_list_ggH125_gamgam[:1]
}
#input_list = ['/nfs/slac/g/atlas/u02/cmilke/mc16-xAOD-ntuple-maker/run/submitDir/data-ANALYSIS/sample.root']

_branch_list = [
    'eventWeight',
    ('truth_particles',  ['tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm']),
    ('truth_jets', ['truthjpT', 'truthjeta', 'truthjphi', 'truthjm']),
    ('reco_jets',  ['tj0pT', 'j0truthid', 'j0_isTightPhoton', 'j0_isPU', 
                        'j0_JVT', 'j0_fJVT_Loose', 'j0_fJVT_Tight', 'j0pT', 'j0eta', 'j0phi', 'j0m'])
]

branch_list = [
    'eventWeight',
    'tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm',
    'truthjpT', 'truthjeta', 'truthjphi', 'truthjm',
    'tj0pT', 'j0truthid', 'j0_isTightPhoton', 'j0_isPU', 
    'j0_JVT', 'j0_fJVT_Loose', 'j0_fJVT_Tight', 'j0pT', 'j0eta', 'j0phi', 'j0m'
]
Nevents = 100

def test(input_type):

    input_list = _input_type_options[input_type]

    raw_reco = []
    for ntuple_file in input_list:
        print('\nnutple file: ' + ntuple_file)
        tree = uproot.rootio.open(ntuple_file)['Nominal']
        tree_iterator = tree.iterate(branches=branch_list, entrysteps=10000) 
        for basket_number, basket in enumerate(tree_iterator):
            for i in range(Nevents):
                tps = []
                for j in range( len(basket[b'tpartpT'][i]) ):
                    Tpt = basket[b'tpartpT'][i][j]
                    Teta = basket[b'tparteta'][i][j]
                    Tphi = basket[b'tpartphi'][i][j]
                    Tm = basket[b'tpartm'][i][j]
                    TpdgID = basket[b'tpartpdgID'][i][j]
                    Tstatus = basket[b'tpartstatus'][i][j]
                    tps.append( (Tpt, Teta, Tphi, Tm, TpdgID, Tstatus) )

                rjs = []
                for j in range( len(basket[b'j0pT'][i]) ):
                    RJpt = basket[b'j0pT'][i][j]
                    RJeta = basket[b'j0eta'][i][j]
                    RJphi = basket[b'j0phi'][i][j]
                    RJm = basket[b'j0m'][i][j]
                    RJpdgID = basket[b'j0truthid'][i][j]
                    rjs.append( (RJpt, RJeta, RJphi, RJm, RJpdgID) )
                raw_reco.append(rjs)
            break
        break



    fancy_reco = []
    for event in event_iterator(input_list, 'Nominal', _branch_list, Nevents):
        rjs = [ ( rj['j0pT'], rj['j0eta'], rj['j0phi'], rj['j0m'], rj['j0truthid'] ) for rj in event['reco_jets'] ]
        fancy_reco.append(rjs)

    for raw, fancy in zip(raw_reco, fancy_reco):
        print(raw)
        print(fancy)
        print()
        

test('sig')
