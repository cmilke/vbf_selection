import sys
import pickle

input_type = sys.argv[1]

processed_output = {2:[], 3:[], 4:[], 5:[], 6:[], 7:[]}
unprocessed_input = pickle.load( open('data/inputs_'+input_type+'_truth.p', 'rb') )

for jet_count, event_list in unprocessed_input.items():
    for event_count, event in enumerate(event_list):
        #if event_count >= 100: break

        #is_truth_quark, pt, eta, phi, m = jet
        #select two highest pt jets
        processed_event = sorted( event, reverse=True, key=(lambda x: x[1]) ) #sort by pt, highest first
        for jet in processed_event[:2]: jet.append(True) #label the first two (highest pt) jets as VBF
        for jet in processed_event[2:]: jet.append(False) #and the rest as not
        processed_output[jet_count].append(processed_event)
for key,value in processed_output.items(): print( '{}: {}'.format(key, len(value) ) )
#print()
#for key,value in processed_output.items():
#    print(key)
#    for event in value: print(event)
#    print()
pickle.dump( processed_output, open('data/processed_inputs_'+input_type+'_truth.p', 'wb') )
