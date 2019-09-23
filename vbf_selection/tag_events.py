import sys
import math
import pickle
from vbf_backend.cmilke_jets import cmilke_jet

input_type = sys.argv[1]

tagger_output = [ [] for i in range(4) ]
processed_input = pickle.load( open('data/processed_input_'+input_type+'.p', 'rb') )

for jet_count, event_list in enumerate(processed_input):
    for event_count, event in enumerate(event_list):
        #if event_count >= 20: break
        vbf_eta_couple = []
        for jet in event:
            if jet.is_marked_vbf: vbf_eta_couple.append(jet.eta)
        if len(vbf_eta_couple) != 2:
            raise RuntimeError('Why do you have {} VBF jets in your event??'.format(len(vbf_eta_couple)))

        delta_eta = abs(vbf_eta_couple[0]-vbf_eta_couple[1])
        if jet_count < len(tagger_output): tagger_output[jet_count].append(delta_eta)

for index,value in enumerate(tagger_output): print( '{}: {}'.format(index, len(value) ) )
#print()
#for index,value in enumerate(tagger_output):
#    print(value)
#    print()
pickle.dump( tagger_output, open('data/tagged_'+input_type+'.p', 'wb') )
