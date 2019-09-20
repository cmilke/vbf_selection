import sys
import math
import pickle

tagger_output = {2:[], 3:[]}
processed_input = pickle.load( open('data/processed_inputs_signal_truth.p', 'rb') )

for jet_count, event_list in processed_input.items():
    for event_count, event in enumerate(event_list):
        vbf_eta_couple = []
        for jet in event:
            is_truth_quark, pt, eta, phi, m, is_marked_vbf = jet
            if is_marked_vbf: vbf_eta_couple.append(eta)
        if len(vbf_eta_couple) != 2:
            raise RuntimeError('Why do you have {} VBF jets in your event??'.format(len(vbf_eta_couple)))

        delta_eta = abs(vbf_eta_couple[0]-vbf_eta_couple[1])
        if jet_count in tagger_output: tagger_output[jet_count].append(delta_eta)
        #if event_count >= 20: break
for key,value in tagger_output.items(): print( '{}: {}'.format(key, len(value) ) )
#print()
#for key,value in tagger_output.items():
#    print(key)
#    for event in value: print(event)
#    print()
pickle.dump( tagger_output, open('data/tagged_signal_truth.p', 'wb') )
