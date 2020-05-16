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


def prepare_tuple(vector_list):
    mjj_deta_pair_list = [ ( (i+j).mass, abs(i.eta-j.eta) ) for i,j in itertools.combinations(vector_list, 2) ]
    if len(mjj_deta_pair_list) > 0:
        mjj_deta_pair_list.sort(reverse=True)
        leading_pair = mjj_deta_pair_list[0]
        return leading_pair
    else:
        return (-1,-1)


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
    events = event_iterator([filename], 'VBF_tree', _output_branches, num_events)
    feature_list = [ make_data_tuple(event) for event in events if event['njets'] - event['ntag'] > 1 ]
    label_list = [label]*len(feature_list)
    return (feature_list, label_list)


def dump_features(bdt, filename):
    feature_list = [ make_data_tuple(event) for event in event_iterator([filename], 'VBF_tree', _output_branches, None) ]
    prediction_array = bdt.decision_function( numpy.array(feature_list) )
    return prediction_array


def train_bdt(dump_event_discriminants):
    num_events = 1000
    train_limit = int( num_events * (3/4) )
    #bgd_vbf_data = uproot.open('../output/V4/output_MC16d_ggF-HH-bbbb.root')['VBF_tree']

    bgd_feature_list, bgd_label_list = get_feature_and_labels('../output/V4/output_MC16d_ggF-HH-bbbb.root', num_events, 0)
    sig_feature_list, sig_label_list = get_feature_and_labels('../output/V4/output_MC16d_VBF-HH-bbbb_cvv1.root', num_events, 1)

    train_feature_array = numpy.array( bgd_feature_list[:train_limit] + sig_feature_list[:train_limit] )
    train_label_array = numpy.array( bgd_label_list[:train_limit] + sig_label_list[:train_limit] )
    test_feature_array = numpy.array( bgd_feature_list[train_limit:] + sig_feature_list[train_limit:] )
    test_label_array = numpy.array( bgd_label_list[train_limit:] + sig_label_list[train_limit:] )
        

    # Create and fit an AdaBoosted decision tree
    bdt = AdaBoostClassifier(
        DecisionTreeClassifier(max_depth=5),
        algorithm="SAMME",
        n_estimators=200
    )

    bdt.fit(train_feature_array, train_label_array)

    predictions = bdt.predict(test_feature_array)
    correct = predictions == test_label_array
    correct_count = numpy.count_nonzero(correct)
    efficiency = correct_count / len(correct)
    decisions = bdt.decision_function( numpy.array(test_feature_array) )
    decision_spread = numpy.histogram(decisions, bins = 1000, range = ( min(decisions), max(decisions) ) )[0]
    spread_factor = numpy.count_nonzero(decision_spread) / len(decision_spread) 
    print('Efficiency: ' + str(efficiency) )
    print('Spread: ' + str(spread_factor) )

    return

    if dump_event_discriminants:
        dump_dictionary = {
            -1: dump_features(bdt, '../output/V4/output_MC16d_ggF-HH-bbbb.root'),
            1: dump_features(bdt, '../output/V4/output_MC16d_VBF-HH-bbbb_cvv1.root')
        }
        pickle.dump( dump_dictionary, open('prediction_dump.p', 'wb') )
    else:
        pickle.dump( bdt, open('trained_bdt.p', 'wb') )


if __name__ == "__main__": train_bdt( len(sys.argv)>1 )
