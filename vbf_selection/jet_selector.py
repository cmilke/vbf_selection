import sys
import pickle
from vbf_backend.cmilke_jets import cmilke_jet

input_type = sys.argv[1]

unprocessed_input = pickle.load( open('data/input_'+input_type+'.p', 'rb') )
processed_output = {
    '2': []
  , '3': []
  , '3 with PU': []
  , '4': []
  , '4 with PU': []
}

for jet_type, event_list in unprocessed_input.items():
    for event_count, event in enumerate(event_list):
        #if event_count >= 100: break

        #select two highest pt jets
        processed_event = sorted( event, reverse=True, key=(lambda x: x.pt) ) #sort by pt, highest first
        for jet in processed_event[:2]:
            jet.is_marked_vbf = True #label the first two (highest pt) jets as VBF
        processed_output[jet_type].append(processed_event)

#for key,value in processed_output.items():
#    print(key)
#    for event in value:
#        for jet in event: print(jet)
#        print()
#    print()
for key,value in processed_output.items(): print( '{}: {}'.format(key, len(value) ) )
pickle.dump( processed_output, open('data/processed_input_'+input_type+'.p', 'wb') )
