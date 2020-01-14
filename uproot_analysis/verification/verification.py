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


def pdgID(vector_to_match, truth_particles):
    for tp in truth_particles:
        if tp['tpartpdgID'] == autils.PDG['photon']:
            if tp['tpartstatus'] != autils.Status['photon_out']: continue
        elif tp['tpartstatus'] != autils.Status['outgoing']: continue

        truth_vec = TLorentzVector.from_ptetaphim(tp['tpartpT'], tp['tparteta'], tp['tpartphi'], tp['tpartm'])

        deltaR = vector_to_match.delta_r(truth_vec)
        if deltaR < 0.3: return tp['tpartpdgID']
    return -1


def test(input_type):

    input_list = _input_type_options[input_type]
    final = []
    for event in event_iterator(input_list, 'Nominal', _branch_list, 10000):
        #tp = list(event['truth_particles'])
        tps = [ tp.copy() for tp in event['truth_particles'] ]

        vs = []
        for rj in event['reco_jets']:
            if not (rj['j0pT'] > 30 and abs(rj['j0eta']) < 4 ): continue
            if not (rj['j0_JVT'] and rj['j0_fJVT_Tight']): continue
            v = TLorentzVector.from_ptetaphim(rj['j0pT'], rj['j0eta'], rj['j0phi'], rj['j0m'])
            ID = pdgID(v,tps)
            #ID = rj['j0truthid']
            #if ID != 22:
            if not rj['j0_isTightPhoton']:
                vs.append( ID in range(1,7) )

        #print( vs )
        #print( [ tp['tpartpdgID'] for tp in tps ] )
        #print(vs.count(1))
        if len(vs) == 3 and vs.count(1) == 2: final.append( vs[0] and vs[1] )
    #print(final)
    print( final.count(1) / len(final) )
        

test('sig')
