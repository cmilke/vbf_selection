import sys
import itertools
import numpy
import pickle
from uproot_wrapper import event_iterator
from uproot_methods import TLorentzVector as LV

from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import make_gaussian_quantiles

_output_branches = [
    'run_number', 'event_number', 'mc_sf', 'ntag', 'njets',
    'n_vbf_candidates',
    ('jets', ['vbf_candidates_E', 'vbf_candidates_pT', 'vbf_candidates_eta', 'vbf_candidates_phi'])
]


#def prepare_tuple(vector_list):
#    mjj_deta_pair_list = [ ( (i+j).mass, abs(i.eta-j.eta) ) for i,j in itertools.combinations(vector_list, 2) ]
#    if len(mjj_deta_pair_list) > 0:
#        mjj_deta_pair_list.sort(reverse=True)
#        prepared_tuple = (
#            mjj_deta_pair_list[0][0],
#            mjj_deta_pair_list[0][1]
#        )
#    else:
#        prepared_tuple = (-1,-1)
#    return prepared_tuple


def prepare_tuple(vector_list):
    if len(vector_list) > 1:
        mjj_deta_pair_list = [ ( (i+j).mass, abs(i.eta-j.eta) ) for i,j in itertools.combinations(vector_list, 2) ]
        mjj_deta_pair_list.sort(reverse=True)
        vector_list.sort(key=lambda vec: vec.pt, reverse=True)
        prepared_tuple = (
            vector_list[0].pt,
            vector_list[0].eta,
            vector_list[0].phi,
            vector_list[0].E,
            vector_list[1].pt,
            vector_list[1].eta,
            vector_list[1].phi,
            vector_list[1].E,
            mjj_deta_pair_list[0][0],
            mjj_deta_pair_list[0][1],
        )
    else:
        prepared_tuple = tuple([-1]*10)
    return prepared_tuple


def make_data_tuple(event):
    vector_list  = []
    for jet in event['jets']:
        vec = LV.from_ptetaphie(
            jet['vbf_candidates_pT'],
            jet['vbf_candidates_eta'],
            jet['vbf_candidates_phi'],
            jet['vbf_candidates_E']
        )
        vector_list.append(vec)

    return( prepare_tuple(vector_list) )


def get_feature_and_labels(filename, num_events, label):
    feature_list, label_list, weight_list = [], [], []
    for event in event_iterator([filename], 'VBF_tree', _output_branches, num_events):
        if event['njets'] - event['ntag'] > 1:
            feature_list.append( make_data_tuple(event) )
            label_list.append(label)
            weight = event['mc_sf'][0] 
            if weight < 0: weight = 0
            weight_list.append(weight)
    return (feature_list, label_list, weight_list)


def dump_features(bdt, filename):
    feature_list = [ make_data_tuple(event) for event in event_iterator([filename], 'VBF_tree', _output_branches, None) ]
    prediction_array = bdt.decision_function( numpy.array(feature_list) )
    return prediction_array


def train_bdt(dump_event_discriminants):
    num_events = 2000
    train_limit = int( num_events * (3/4) )
    #bgd_vbf_data = uproot.open('../output/V4/output_MC16d_ggF-HH-bbbb.root')['VBF_tree']

    bgd_data = get_feature_and_labels('../output/V4/output_MC16d_ggF-HH-bbbb.root', num_events, 0)
    sig_data = get_feature_and_labels('../output/V4/output_MC16d_VBF-HH-bbbb_cvv1.root', num_events, 1)

    training_arrays = [ bgd[:train_limit]+sig[:train_limit] for bgd,sig in zip(bgd_data, sig_data) ]
    testing_arrays = [ bgd[train_limit:]+sig[train_limit:] for bgd,sig in zip(bgd_data, sig_data) ]

    train_features, train_labels, train_weights = training_arrays
    test_features, test_labels, test_weights = testing_arrays
        

    # Create and fit an AdaBoosted decision tree
    bdt = AdaBoostClassifier(
        DecisionTreeClassifier(max_depth=10),
        algorithm="SAMME",
        n_estimators=300
    )

    print('\nFitting BDT..')
    #bdt.fit(train_features, train_labels)
    bdt.fit(train_features, train_labels, sample_weight=train_weights)

    predictions = bdt.predict(test_features)
    correct = predictions==test_labels
    efficiency = sum(correct) / len(predictions)
    weighted_efficiency = sum(correct*test_weights)  / sum(test_weights)

    decisions = bdt.decision_function(test_features)
    decision_spread = numpy.histogram(decisions, bins = 10000, range = ( min(decisions), max(decisions) ) )[0]
    spread_factor = numpy.count_nonzero(decision_spread)
    print('Efficiency: ' + str(efficiency) )
    print('Weighted Efficiency: ' + str(weighted_efficiency) )
    print('Spread: ' + str(spread_factor) ) # You want something over ~300

    dump_bdt = False

    if dump_event_discriminants:
        dump_dictionary = {
            -1: dump_features(bdt, '../output/V4/output_MC16d_ggF-HH-bbbb.root'),
            1: dump_features(bdt, '../output/V4/output_MC16d_VBF-HH-bbbb_cvv1.root')
        }
        pickle.dump( dump_dictionary, open('prediction_dump.p', 'wb') )
    elif dump_bdt:
        pickle.dump( bdt, open('trained_bdt.p', 'wb') )


if __name__ == "__main__": train_bdt( len(sys.argv)>1 )
