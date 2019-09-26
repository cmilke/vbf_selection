import sys
import math
import pickle
from vbf_backend.cmilke_jets import cmilke_jet
from vbf_backend import basic_vbf_tagging_algorithms

def tag_events(input_type, tagger):
    tagger_output = {
        '2_2maxpt': []
      , '3_2maxpt': []
      , '3inclPU_2maxpt': []
    }

    jet_input = pickle.load( open('data/input_'+input_type+'.p', 'rb') )
    selector_input = pickle.load( open('data/jet_selections_'+input_type+'.p', 'rb') )

    for jet_type, event_list in jet_input.items():
        for event_count, event in enumerate(event_list):
            #if event_count >= 20: break
            for algorithm, selections in selector_input[jet_type].items():
                tag_label = jet_type + '_' + algorithm
                if tag_label not in tagger_output: continue

                vbf_jets = selections[event_count]
                discriminant = tagger(event,vbf_jets)
                tagger_output[tag_label].append(discriminant)

    #for key,value in tagger_output.items():
    #    print(key, value)
    #    print()
    for key,value in tagger_output.items(): print( '{}: {}'.format(key, len(value) ) )
    pickle.dump( tagger_output, open('data/tagged_'+tagger_name+'_'+input_type+'.p', 'wb') )


available_taggers = {
    'delta_eta': basic_vbf_tagging_algorithms.delta_eta_tagger
  , 'mjj': basic_vbf_tagging_algorithms.mjj_tagger
  , 'mjjj': basic_vbf_tagging_algorithms.mjjj_tagger
}

input_type = sys.argv[1]
tagger_name = sys.argv[2]
tagger = available_taggers[tagger_name]

if input_type == 'all':
    tag_events('bgd', tagger)
    print()
    tag_events('sig', tagger)
else:
    tag_events(input_type, tagger)
