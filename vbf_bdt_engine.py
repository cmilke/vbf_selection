import sys
import itertools
import numpy
import pickle
from functools import partial

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

import uproot
from uproot_methods import TLorentzVector as LV

from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import make_gaussian_quantiles
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

from uproot_wrapper import event_iterator
from plotting_utils import Hist1, Roc



_output_branches = [
    'run_number', 'event_number', 'mc_sf', 'ntag', 'njets',
    'n_vbf_candidates', 'vbf_candidates_E', 'vbf_candidates_pT', 'vbf_candidates_eta', 'vbf_candidates_phi'
]
_output_branches+=[f'FoxWolfram{i}' for i in range(1,11)]

_fourvec_names = [ f'vbf_candidates_{v}' for v in ['pT', 'eta', 'phi', 'E'] ]

make_vector_list = lambda datarow: [ LV.from_ptetaphie(*vec) for vec in zip(*datarow[_fourvec_names]) ]



def get_features_mjj_deta(datarow):
    vector_list = make_vector_list(datarow)
    pair_list = [ (i,j) for i,j in itertools.combinations(vector_list, 2) ]
    if len(pair_list) > 0:
        mjj_deta_pair_list = [ ( (i+j).mass, abs(i.eta-j.eta) ) for i,j in pair_list]
        mjj_deta_pair_list.sort(reverse=True)
        prepared_features = [
            mjj_deta_pair_list[0][0],
            mjj_deta_pair_list[0][1]
        ]
    else:
        prepared_features = [-1,-1]
    return prepared_features



def get_features_mjj_deta_fw(datarow):
    vector_list = make_vector_list(datarow)
    pair_list = [ (i,j) for i,j in itertools.combinations(vector_list, 2) ]
    if len(pair_list) > 0:
        mjj_deta_pair_list = [ ( (i+j).mass, abs(i.eta-j.eta) ) for i,j in pair_list]
        mjj_deta_pair_list.sort(reverse=True)
        feature_list = [
            mjj_deta_pair_list[0][0],
            mjj_deta_pair_list[0][1]
        ]
        feature_list += [ datarow[f'FoxWolfram{fwi}'] for fwi in range(1,8) ]
    else:
        feature_list = [-1]*9
    return feature_list



def get_feature_and_labels(dataframe, feature_extractor, num_events, label):
    print(f'Retrieving {label} features...')
    if num_events != None:
        dataframe = dataframe[:num_events]
        dataframe = dataframe[ dataframe['njets']-dataframe['ntag'] > 1 ]
    features = numpy.asarray( dataframe.apply(feature_extractor, axis=1).tolist() )
    labels = numpy.full(len(features), label)
    weights = dataframe['mc_sf'].apply(lambda x: x[0] if x[0] > 0 else 0).to_numpy()
    return {'X':features, 'y':labels, 'sample_weight':weights}



def train_classifier(mode, data, ML_classifier, n_events, **kwargs):
    train_limit, test_limit = n_events
    test_limit += train_limit
    training_data = { key:numpy.concatenate( (data[0][key][:train_limit], data[1][key][:train_limit]) ) for key in data[0].keys() }

    # Fit ML classifier
    print('Fitting BDT..')
    ML_classifier.fit(**training_data)

    if mode == 'train':
        print('Evaluating Performance...')
        decisions = [ ML_classifier.decision_function(d['X']) for d in data ]
        weights = [ d['sample_weight'][train_limit:] for d in data ]
        overtrain_check = Hist1('BDT/ot-check_'+kwargs['title'], 'Overtraining Check', [], 40, (-0.5,0.5))
        overtrain_check.generate_plot({
            'B-Train':decisions[0][:train_limit],
            'S-Train':decisions[1][:train_limit],
            'B-Test' :decisions[0][train_limit:],
            'S-Test' :decisions[1][train_limit:]
        })
        plot_importance( kwargs['title'], ML_classifier, kwargs['feature_labels'] )
        return ( (decisions[1][train_limit:],weights[1]), (decisions[0][train_limit:],weights[0]) )

    elif mode == 'dump_scores':
        dump_dictionary = {
            -1: ML_classifier.decision_function( data[0]['X'] ),
             1: ML_classifier.decision_function( data[1]['X'] )
        }
        pickle.dump( dump_dictionary, open('prediction_dump_'+kwargs['dump_name']+'.p', 'wb') )

    else:
        pickle.dump( ML_classifier, open('trained_classifier.p', 'wb') )



def plot_importance( plot_name, ML_classifier, feature_labels):
    feature_tuple = list(zip( ML_classifier.feature_importances_, feature_labels ))
    feature_tuple.sort(reverse=True)
    feature_importance = {key:val for val,key in feature_tuple}
    bin_indices = list(range(len(feature_importance)))
    bin_edges = bin_indices + [len(bin_indices)]

    counts, bins, hist = plt.hist(bin_indices, bins=bin_edges, weights=list(feature_importance.values()), rwidth=.7)
    #plt.xlabel('(n truth, n reco)')
    #plt.ylabel('Fraction')
    plt.title('Importance of Features in Classifier')
    plt.xticks(ticks=(numpy.array(bin_indices)+0.5), labels=feature_importance.keys())
    plt.savefig('figures/BDT/feature-importance_'+plot_name+'.png')
    plt.close()



def hyper_parameter_scan(input_frames):
    evaluation_table = {}
    test_limit = 15000

    # Simple mjj & Delta eta BDT
    data = [ get_feature_and_labels(input_frames[i], get_features_mjj_deta, test_limit, i) for i in (0,1) ]
    for n_events in [(10000,5000)]:
        for depth in [4]:
            for estimators in [500]:
                adatree = AdaBoostClassifier( DecisionTreeClassifier(max_depth=depth), algorithm="SAMME", n_estimators=estimators)
                print(f'Training mjj-Deta BDT with Nevts={n_events}, depth={depth}, and estimators={estimators}')
                evaluation_data = train_classifier('train', data, adatree, n_events,
                        title='mjj_deta', feature_labels=['mjj','Deta'])
                evaluation_table[f'mjj-Deta: Nevts={n_events}, depth={depth}, Nest={estimators}'] = evaluation_data

    # mjj & Delta eta w/ Fox Wolfram Moments
    data = [ get_feature_and_labels(input_frames[i], get_features_mjj_deta_fw, test_limit, i) for i in (0,1) ]
    for n_events in [(10000,5000)]:
        for depth in [3,4,5]:
            for estimators in [500]:
                adatree = AdaBoostClassifier( DecisionTreeClassifier(max_depth=depth), algorithm="SAMME", n_estimators=estimators)
                print(f'Training new mjj-Deta-FW BDT with n_events={n_events}, depth={depth}, and estimators={estimators}')
                evaluation_data = train_classifier('train', data, adatree, n_events,
                    title=f'mjj_deta_FW_{depth}', feature_labels=['mjj','Deta']+[ f'FW{i}' for i in range(1,8) ] )
                evaluation_table[f'mjj-Deta-FW: Nevnt={n_events}, depth={depth}, Nest={estimators}'] = evaluation_data


    print('Plotting final performance ROCs')
    roc_curve = Roc( 'BDT/BDT_evaluation_results', 'Weighted Efficiency/Rejection Performance\nof BDT Using Varying Hyperparameters', evaluation_table.keys() )
    roc_curve.generate_plot(evaluation_table) 


if __name__ == "__main__":
    print('Loading Data...')
    data_files = ['../output/V5/output_MC16d_ggF-HH-bbbb.root', '../output/V5/output_MC16d_VBF-HH-bbbb_cvv1.root']
    input_frames = [ uproot.open(datafile)['VBF_tree'].pandas.df(branches=_output_branches, flatten=False) for datafile in data_files ]
    if len(sys.argv) == 1:
        print('Beginning scan.')
        hyper_parameter_scan(input_frames)
    else:
        print('Beginning dump.')
        data = [ get_feature_and_labels(input_frames[i], get_features_mjj_deta, None, i) for i in (0,1) ]
        adatree = AdaBoostClassifier( DecisionTreeClassifier(max_depth=4), algorithm="SAMME", n_estimators=500)
        train_classifier('dump_scores', data, adatree, (10000,0), dump_name=sys.argv[1] )
        #data = [ get_feature_and_labels(input_frames[i], get_features_mjj_deta_fw, None, i) for i in (0,1) ]
        #adatree = AdaBoostClassifier( DecisionTreeClassifier(max_depth=3), algorithm="SAMME", n_estimators=500)
        #train_classifier('dump_scores', data, adatree, (10000,0), dump_name=sys.argv[1] )
