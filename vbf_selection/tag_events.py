import sys
import math
import pickle
from vbf_backend.cmilke_jets import cmilke_jet
from vbf_backend.basic_vbf_tagging_algorithms import delta_eta_tagger

input_type = sys.argv[1]

tagger_output = {
    '2, 2maxpt': []
  , '3, 2maxpt': []
  , '3 with PU, 2maxpt': []
}

jet_input = pickle.load( open('data/input_'+input_type+'.p', 'rb') )
selector_input = pickle.load( open('data/jet_selections_'+input_type+'.p', 'rb') )

for jet_type, event_list in jet_input.items():
    for event_count, event in enumerate(event_list):
        #if event_count >= 20: break
        for algorithm, selections in selector_input[jet_type].items():
            tag_label = jet_type + ', ' + algorithm
            if tag_label not in tagger_output: continue

            vbf_jets = selections[event_count]
            discriminant = delta_eta_tagger(event,vbf_jets)
            tagger_output[tag_label].append(discriminant)

#for key,value in tagger_output.items():
#    print(key, value)
#    print()
for key,value in tagger_output.items(): print( '{}: {}'.format(key, len(value) ) )
pickle.dump( tagger_output, open('data/tagged_'+input_type+'.p', 'wb') )
