import sys
import math
import pickle
from vbf_backend.cmilke_jets import cmilke_jet

input_type = sys.argv[1]

tagger_output = {
    '2': []
  , '3': []
  , '3 with PU': []
  #, '4': []
  #, '4 with PU': []
}
processed_input = pickle.load( open('data/processed_input_'+input_type+'.p', 'rb') )

for jet_type, event_list in processed_input.items():
    print(jet_type)
    for event_count, event in enumerate(event_list):
        #if event_count >= 20: break
        vbf_eta_couple = []
        for jet in event:
            if jet.is_marked_vbf: vbf_eta_couple.append(jet.eta)
        if len(vbf_eta_couple) != 2:
            raise RuntimeError('Why do you have {} VBF jets in your event??'.format(len(vbf_eta_couple)))

        delta_eta = abs(vbf_eta_couple[0]-vbf_eta_couple[1])
        if jet_type in tagger_output: tagger_output[jet_type].append(delta_eta)

#for key,value in tagger_output.items():
#    print(key, value)
#    print()
for key,value in tagger_output.items(): print( '{}: {}'.format(key, len(value) ) )
pickle.dump( tagger_output, open('data/tagged_'+input_type+'.p', 'wb') )
