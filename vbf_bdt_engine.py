import sys
import numpy
import pickle

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import uproot

from sklearn.ensemble import AdaBoostClassifier
import sklearn.tree
#from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import make_gaussian_quantiles
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

from uproot_wrapper import event_iterator
from plotting_utils import Hist1, Roc
from feature_extractors import Extractors
from koza4ok.skTMVA import convert_bdt_sklearn_tmva



_output_branches = [
    'run_number', 'event_number', 'mc_sf', 'ntag', 'njets',
    'n_vbf_candidates', 'vbf_candidates_E', 'vbf_candidates_pT', 'vbf_candidates_eta', 'vbf_candidates_phi'
]
_output_branches+=[f'FoxWolfram{i}' for i in range(1,11)]



def get_feature_and_labels(dataframe, feature_extractor, num_events, label):
    print(f'Retrieving {label} features...')
    if num_events != None:
        dataframe = dataframe[:num_events]
        dataframe = dataframe[ dataframe['njets']-dataframe['ntag'] > 1 ]
    features = numpy.asarray( dataframe.apply(feature_extractor, axis=1).tolist() )
    labels = numpy.full(len(features), label)
    weights = dataframe['mc_sf'].apply(lambda x: x[0] if x[0] > 0 else 0).to_numpy()
    return {'X':features, 'y':labels, 'sample_weight':weights}



def plot_classifier_details(ML_classifier, decisions, train_limit, title, feature_labels):
    # Plot Overtraining Check
    overtrain_check = Hist1('BDT/ot-check_'+title, 'Overtraining Check', [], 40, (-0.5,0.5))
    overtrain_check.generate_plot({
        'B-Train':decisions[0][:train_limit],
        'S-Train':decisions[1][:train_limit],
        'B-Test' :decisions[0][train_limit:],
        'S-Test' :decisions[1][train_limit:]
    })

    # Plot Feature Ranking
    print('Plotting feature ranks...')
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
    plt.savefig('figures/BDT/feature-importance_'+title+'.png')
    plt.close()

    # Draw BDT Structure
    print('Plotting tree structures...')
    output = PdfPages('figures/BDT/tree-structures_'+title+'.pdf')
    for estimator in ML_classifier.estimators_[:10]:
        plt.figure()
        sklearn.tree.plot_tree(estimator,
             feature_names=list(feature_importance.keys()),
             class_names=['ggF', 'VBF'],
             filled=True, rounded=True)
        output.savefig(bbox_inches='tight')
        plt.close()
    output.close()



def train_classifier(data, ML_classifier, n_events, **kwargs):
    train_limit, test_limit = n_events
    test_limit += train_limit
    training_data = { key:numpy.concatenate( (data[0][key][:train_limit], data[1][key][:train_limit]) ) for key in data[0].keys() }

    # Fit ML classifier
    print('Fitting BDT..')
    ML_classifier.fit(**training_data)

    print('Evaluating Performance...')
    decisions = [ ML_classifier.decision_function(d['X']) for d in data ]
    weights = [ d['sample_weight'][train_limit:] for d in data ]
    plot_classifier_details( ML_classifier, decisions, train_limit, kwargs['title'], kwargs['feature_labels'])

    print('Saving Classifier...') # Output as pickled file (for local analysis) and as xml (for use in Resolved Reconstruction)
    pickle.dump( ML_classifier, open('bdt_output/trained_classifier_'+kwargs['title']+'.p', 'wb') )
    input_format = [ (label, 'F') for label in kwargs['feature_labels'] ]
    convert_bdt_sklearn_tmva(ML_classifier, input_format, 'bdt_output/trained_classifier_'+kwargs['title']+'.xml')

    # Return overall performance for comparison against other architectures
    return ( (decisions[1][train_limit:],weights[1]), (decisions[0][train_limit:],weights[0]) )


def hyper_parameter_scan(input_frames):
    evaluation_table = {}
    test_limit = 1500

    ## Simple mjj & Delta eta BDT
    #data = [ get_feature_and_labels(input_frames[i], Extractors['mjj-Deta'], test_limit, i) for i in (0,1) ]
    #for n_events in [(10000,5000)]:
    #    for depth in [4]:
    #        for estimators in [500]:
    #            adatree = AdaBoostClassifier( DecisionTreeClassifier(max_depth=depth), algorithm="SAMME", n_estimators=estimators)
    #            print(f'\nTraining mjj-Deta BDT with Nevts={n_events}, depth={depth}, and estimators={estimators}')
    #            evaluation_data = train_classifier('train', data, adatree, n_events,
    #                    title='mjj_deta', feature_labels=['mjj','Deta'])
    #            evaluation_table[f'mjj-Deta: Nevts={n_events}, depth={depth}, Nest={estimators}'] = evaluation_data

    # mjj & Delta eta w/ Fox Wolfram Moments
    data = [ get_feature_and_labels(input_frames[i], Extractors['mjj-Deta-FW'], test_limit, i) for i in (0,1) ]
    for n_events in [(1000,500)]:
        for depth in [3]:
            for estimators in [500]:
                adatree = AdaBoostClassifier( sklearn.tree.DecisionTreeClassifier(max_depth=depth), algorithm="SAMME", n_estimators=estimators)
                print(f'\nTraining new mjj-Deta-FW BDT with n_events={n_events}, depth={depth}, and estimators={estimators}')
                evaluation_data = train_classifier( data, adatree, n_events,
                    title=f'mjj_deta_FW_{depth}', feature_labels=['mjj','Deta']+[ f'FW{i}' for i in range(1,8) ] )
                evaluation_table[f'mjj-Deta-FW: Nevnt={n_events}, depth={depth}, Nest={estimators}'] = evaluation_data


    ## mjj & Delta eta w/ Fox Wolfram Moments and Centrality
    #data = [ get_feature_and_labels(input_frames[i], Extractors['mjj-Deta-FW-Cent'], test_limit, i) for i in (0,1) ]
    #for n_events in [(10000,5000)]:
    #    for depth in [3,4]:
    #        for estimators in [500]:
    #            adatree = AdaBoostClassifier( sklearn.tree.DecisionTreeClassifier(max_depth=depth), algorithm="SAMME", n_estimators=estimators)
    #            print(f'\nTraining new mjj-Deta-FW-Centrality BDT with n_events={n_events}, depth={depth}, and estimators={estimators}')
    #            evaluation_data = train_classifier( data, adatree, n_events,
    #                title=f'mjj_deta_FW_Cent{depth}', feature_labels=['mjj','Deta']+[ f'FW{i}' for i in range(1,8) ]+['Cent.'] )
    #            evaluation_table[f'mjj-Deta-FW-Cent: Nevnt={n_events}, depth={depth}, Nest={estimators}'] = evaluation_data


    ## mjj and mjjSL & Delta eta w/ Fox Wolfram Moments and Centrality
    #data = [ get_feature_and_labels(input_frames[i], Extractors['mjjLSL-Deta-Cent-FW'], test_limit, i) for i in (0,1) ]
    #for n_events in [(10000,5000)]:
    #    for depth in [3,4]:
    #        for estimators in [500]:
    #            adatree = AdaBoostClassifier( sklearn.tree.DecisionTreeClassifier(max_depth=depth), algorithm="SAMME", n_estimators=estimators)
    #            print(f'\nTraining new mjjL,SL-Deta-Centrality-FW BDT with n_events={n_events}, depth={depth}, and estimators={estimators}')
    #            evaluation_data = train_classifier( data, adatree, n_events,
    #                title=f'mjjLSL_deta_Cent_FW{depth}', feature_labels=['mjj','Deta','mjjSL','DetaSL', 'Cent']+[ f'FW{i}' for i in range(1,8) ] )
    #            evaluation_table[f'mjjLSL-Deta-Cent-FW: Nevnt={n_events}, depth={depth}, Nest={estimators}'] = evaluation_data


    print('\nPlotting final performance ROCs')
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
        bdt_name = sys.argv[1]
        extraction_name =sys.argv[2]
        data = [ get_feature_and_labels(input_frames[i], Extractors[extraction_name], None, i) for i in (0,1) ]
        ML_classifier = pickle.load(open('bdt_output/trained_classifier_'+bdt_name+'.p', 'rb'))
        dump_dictionary = {
            -1: ML_classifier.decision_function( data[0]['X'] ),
             1: ML_classifier.decision_function( data[1]['X'] )
        }
        pickle.dump( dump_dictionary, open('bdt_output/prediction_dump_'+extraction_name+'.p', 'wb') )
