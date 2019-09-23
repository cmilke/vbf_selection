import sys
import pickle
from vbf_backend.cmilke_jets import cmilke_jet

input_type = sys.argv[1]

unprocessed_input = pickle.load( open('data/input_'+input_type+'.p', 'rb') )
processed_output = [ [] for i in range( len(unprocessed_input) ) ]

for jet_count, event_list in enumerate(unprocessed_input):
    for event_count, event in enumerate(event_list):
        #if event_count >= 100: break

        #select two highest pt jets
        processed_event = sorted( event, reverse=True, key=(lambda x: x.pt) ) #sort by pt, highest first
        for jet in processed_event[:2]: jet.is_marked_vbf = True #label the first two (highest pt) jets as VBF
        processed_output[jet_count].append(processed_event)

for index,value in enumerate(processed_output): print( '{}: {}'.format(index, len(value) ) )
#print()
#for index,value in enumerate(processed_output):
#    print(index)
#    for event in value:
#        for jet in event: print(jet)
#        print()
#    print()
pickle.dump( processed_output, open('data/processed_input_'+input_type+'.p', 'wb') )
