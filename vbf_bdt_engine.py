import sys
import itertools
import numpy
import pickle
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from uproot_methods import TLorentzVector as LV
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import make_gaussian_quantiles
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

from uproot_wrapper import event_iterator
from plotting_utils import Hist1, Roc



_output_branches = [
    'run_number', 'event_number', 'mc_sf', 'ntag', 'njets',
    'n_vbf_candidates',
    ('jets', ['vbf_candidates_E', 'vbf_candidates_pT', 'vbf_candidates_eta', 'vbf_candidates_phi'])
]
_output_branches+=[f'FoxWolfram{i}' for i in range(1,11)]


def make_vector_list(event):
    vector_list  = []
    for jet in event['jets']:
        vec = LV.from_ptetaphie(
            jet['vbf_candidates_pT'],
            jet['vbf_candidates_eta'],
            jet['vbf_candidates_phi'],
            jet['vbf_candidates_E']
        )
        vector_list.append(vec)
    return vector_list


def get_features_mjj_deta(event):
    vector_list = make_vector_list(event)
    mjj_deta_pair_list = [ ( (i+j).mass, abs(i.eta-j.eta) ) for i,j in itertools.combinations(vector_list, 2) ]
    if len(mjj_deta_pair_list) > 0:
        mjj_deta_pair_list.sort(reverse=True)
        prepared_features = (
            mjj_deta_pair_list[0][0],
            mjj_deta_pair_list[0][1]
        )
    else:
        prepared_features = (-1,-1)
    return prepared_features


def get_features_mjj_deta_fw(event):
    vector_list = make_vector_list(event)
    mjj_deta_pair_list = [ ( (i+j).mass, abs(i.eta-j.eta) ) for i,j in itertools.combinations(vector_list, 2) ]
    if len(mjj_deta_pair_list) > 0:
        mjj_deta_pair_list.sort(reverse=True)
        feature_list = [
            mjj_deta_pair_list[0][0],
            mjj_deta_pair_list[0][1]
        ]
        feature_list += [ event[f'FoxWolfram{fwi}'] for fwi in range(1,8) ]
    else:
        feature_list = [-1]*9
    return feature_list


def get_feature_and_labels(feature_extractor, filename, num_events, label):
    feature_list, label_list, weight_list = [], [], []
    for event in event_iterator([filename], 'VBF_tree', _output_branches, num_events):
        if event['njets'] - event['ntag'] > 1:
            feature_list.append( feature_extractor(event) )
            label_list.append(label)
            weight = event['mc_sf'][0] 
            if weight < 0: weight = 0
            weight_list.append(weight)
    return {'X':feature_list, 'y':label_list, 'sample_weight':weight_list}


def dump_features(feature_extractor, classifier, filename):
    feature_list = [ feature_extractor(event) for event in event_iterator([filename], 'VBF_tree', _output_branches, None) ]
    prediction_array = classifier.decision_function( numpy.array(feature_list) )
    return prediction_array


def train_classifier(mode, feature_extractor, ML_classifier, **kwargs):
    train_limit, test_limit = kwargs['num_events']
    test_limit += train_limit
    #bgd_vbf_data = uproot.open('../output/V4/output_MC16d_ggF-HH-bbbb.root')['VBF_tree']

    bgd_data = get_feature_and_labels(feature_extractor, '../output/V5/output_MC16d_ggF-HH-bbbb.root', test_limit, 0)
    sig_data = get_feature_and_labels(feature_extractor, '../output/V5/output_MC16d_VBF-HH-bbbb_cvv1.root', test_limit, 1)
    training_data = { key:bgd_data[key][:train_limit]+sig_data[key][:train_limit] for key in bgd_data.keys() }

    # Fit ML classifier
    print('\nFitting BDT..')
    ML_classifier.fit(**training_data)

    if mode == 'train':
        # Evaluate performance
        bgd_train_decisions = ML_classifier.decision_function(bgd_data['X'][:train_limit])
        sig_train_decisions = ML_classifier.decision_function(sig_data['X'][:train_limit])
        bgd_decisions = ML_classifier.decision_function(bgd_data['X'][train_limit:test_limit])
        sig_decisions = ML_classifier.decision_function(sig_data['X'][train_limit:test_limit])
        bgd_weights = bgd_data['sample_weight'][train_limit:test_limit]
        sig_weights = sig_data['sample_weight'][train_limit:test_limit]
        overtrain_check = Hist1('BDT/ot-check_'+kwargs['title'], 'Overtraining Check', [], 40, (-0.5,0.5))
        overtrain_check.generate_plot({'B-Train':bgd_train_decisions,'S-Train':sig_train_decisions, 'B-Test':bgd_decisions, 'S-Test':sig_decisions}) 
        plot_importance( kwargs['title'], ML_classifier, kwargs['feature_labels'] )
        return ( (sig_decisions,sig_weights), (bgd_decisions,bgd_weights) )
        #return ( (sig_decisions,[1]*len(sig_decisions)), (bgd_decisions,[1]*len(bgd_decisions)) )

    elif mode == 'dump_scores':
        dump_dictionary = {
            -1: dump_features(feature_extractor, ML_classifier, '../output/V5/output_MC16d_ggF-HH-bbbb.root'),
            1: dump_features(feature_extractor, ML_classifier, '../output/V5/output_MC16d_VBF-HH-bbbb_cvv1.root')
        }
        pickle.dump( dump_dictionary, open('prediction_dump.p', 'wb') )

    else:
        pickle.dump( ML_classifier, open('trained_classifier.p', 'wb') )



def plot_importance( plot_name, ML_classifier, feature_labels):
    feature_tuple = list(zip( ML_classifier.feature_importances_, feature_labels ))
    feature_tuple.sort(reverse=True)
    feature_importance = {key:val for val,key in feature_tuple}
    bin_indices = list(range(len(feature_importance)))
    bin_edges = bin_indices + [len(bin_indices)]

    counts, bins, hist = plt.hist(bin_indices, bins=bin_edges, weights=list(feature_importance.values()), rwidth=.7)
    #plt.xticks(ticks=(bins+0.5), labels=xlabels)
    #plt.xlabel('(n truth, n reco)')
    #plt.ylabel('Fraction')
    #plt.ylim(0, 1.0)
    plt.title('Importance of Features in Classifier')
    plt.xticks(ticks=(numpy.array(bin_indices)+0.5), labels=feature_importance.keys())
    plt.savefig('figures/BDT/feature-importance_'+plot_name+'.png')
    plt.close()



def hyper_parameter_scan():
    evaluation_table = {}

    # Simple mjj & Delta eta BDT
    for n_events in [(10000,5000)]:
        for depth in [4]:
            for estimators in [500]:
                adatree = AdaBoostClassifier(
                    DecisionTreeClassifier(max_depth=depth),
                    algorithm="SAMME",
                    n_estimators=estimators
                )
                print(f'\nTraining new mjj-Deta BDT with n_events={n_events}, depth={depth}, and estimators={estimators}')
                evaluation_data = train_classifier('train', get_features_mjj_deta, adatree, num_events=n_events,
                        title='mjj_deta', feature_labels=['mjj','Deta'])
                evaluation_table[f'mjj-Deta: Nevnt={n_events}, depth={depth}, Nest={estimators}'] = evaluation_data

    # mjj & Delta eta w/ Fox Wolfram Moments
    for n_events in [(10000,5000)]:
        for depth in [3,4,5]:
            for estimators in [500]:
                adatree = AdaBoostClassifier(
                    DecisionTreeClassifier(max_depth=depth),
                    algorithm="SAMME",
                    n_estimators=estimators
                )
                print(f'Training new mjj-Deta-FW BDT with n_events={n_events}, depth={depth}, and estimators={estimators}')
                evaluation_data = train_classifier('train', get_features_mjj_deta_fw, adatree, num_events=n_events,
                    title=f'mjj_deta_FW_{depth}', feature_labels=['mjj','Deta']+[ f'FW{i}' for i in range(1,8) ] )
                evaluation_table[f'mjj-Deta-FW: Nevnt={n_events}, depth={depth}, Nest={estimators}'] = evaluation_data


    print('Evaluating Performance')
    roc_curve = Roc( 'BDT/BDT_evaluation_results', 'Weighted Efficiency/Rejection Performance\nof BDT Using Varying Hyperparameters', evaluation_table.keys() )
    roc_curve.generate_plot(evaluation_table) 


if __name__ == "__main__":
    if len(sys.argv) == 1:
        hyper_parameter_scan()
    else:
        #adatree = AdaBoostClassifier( DecisionTreeClassifier(max_depth=3), algorithm="SAMME", n_estimators=300 )
        #train_classifier('dump_scores', get_features_mjj_deta, adatree, num_events=(10000,0))

        adatree = AdaBoostClassifier( DecisionTreeClassifier(max_depth=3), algorithm="SAMME", n_estimators=1000)
        train_classifier('dump_scores', get_features_mjj_deta_fw, adatree, num_events=(10000,0))
