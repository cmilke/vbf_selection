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


Nevents = 1000


def get_pdgID(vector_to_match, truth_particles):
    for tp in truth_particles:
        if tp['tpartpdgID'] == autils.PDG['photon']:
            if tp['tpartstatus'] != autils.Status['photon_out']: continue
        elif tp['tpartstatus'] != autils.Status['outgoing']: continue

        truth_vec = TLorentzVector.from_ptetaphim(tp['tpartpT'], tp['tparteta'], tp['tpartphi'], tp['tpartm'])

        deltaR = vector_to_match.delta_r(truth_vec)
        if deltaR < 0.3: return tp['tpartpdgID']
    return -1


def get_pdgID_raw(vector_to_match, truth_particles ):
    for tp in truth_particles:
        pt, eta, phi, m, pdgid, status = tp
        if pdgid == autils.PDG['photon']:
            if status != autils.Status['photon_out']: continue
        elif status != autils.Status['outgoing']: continue

        truth_vec = TLorentzVector.from_ptetaphim(pt, eta, phi, m)

        deltaR = vector_to_match.delta_r(truth_vec)
        if deltaR < 0.3: return pdgid
    return -1


def test(input_type):

    input_list = _input_type_options[input_type]
    final = []

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
                
                vs = []
                tmp = []
                for j in range( len(basket[b'j0pT'][i]) ):
                    if not ( basket[b'j0pT'][i][j] > 30 and abs(basket[b'j0eta'][i][j]) < 4 ): continue
                    if not ( basket[b'j0_JVT'][i][j] and basket[b'j0_fJVT_Tight'][i][j]): continue
                    v = TLorentzVector.from_ptetaphim(basket[b'j0pT'][i][j], basket[b'j0eta'][i][j], basket[b'j0phi'][i][j], basket[b'j0m'][i][j])
                    ID = get_pdgID_raw(v,tps)
                    tmp.append(ID)
                    #ID = rj['j0truthid']
                    if ID != 22:
                    #if not basket[b'j0_isTightPhoton'][i][j]:
                        vs.append( ID in range(1,7) )
                if len(vs) == 3 and vs.count(1) == 2: final.append( vs[0] and vs[1] )
            break
        break

    print()

    print( final.count(1) / len(final) )


    final = []
    for event in event_iterator(input_list, 'Nominal', _branch_list, Nevents):
        #tp = list(event['truth_particles'])
        tps = [ tp.copy() for tp in event['truth_particles'] ]
        #for tp in event['truth_particles']: pass

        vs = []
        tmp = []
        for rj in event['reco_jets']:
            if not (rj['j0pT'] > 30 and abs(rj['j0eta']) < 4 ): continue
            if not (rj['j0_JVT'] and rj['j0_fJVT_Tight']): continue
            v = TLorentzVector.from_ptetaphim(rj['j0pT'], rj['j0eta'], rj['j0phi'], rj['j0m'])
            ID = get_pdgID(v,tps)
            #print()
            tmp.append(ID)
            if ID != 22:
            #if not rj['j0_isTightPhoton']:
                vs.append( ID in range(1,7) )
        if len(vs) == 3 and vs.count(1) == 2: final.append( vs[0] and vs[1] )
    print( final.count(1) / len(final) )
        

test('sig')
