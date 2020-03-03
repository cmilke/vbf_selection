#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import pickle
    

def print_event(input_type):
    data_dump = pickle.load( open('data/output_aviv_tag_'+input_type+'.p', 'rb') )

    #events_with_3_jets = [ event for event in data_dump['JVT'].events if len(event.jets) == 3 ]
    for category_key in [ 'JVT', 'JVT_50-30', 'JVT_70-50-30']:#, 'JVT20' ]:
        num_2_jets = 0
        num_3_jets = 0
        all_jets = 0
        for event in data_dump[category_key].events:
            if len(event.jets) == 2: num_2_jets += 1
            else: num_3_jets += 1
            all_jets += 1

        print( category_key+': {}, {}, {}, {:.02f}, {:.02f}'.format(all_jets, num_2_jets, num_3_jets, num_2_jets/all_jets, num_3_jets/all_jets) )


    #num_same = 0
    #for index, event in enumerate(events_with_3_jets):
    #    maxpt_selection = event.selectors['2maxpt'].selections
    #    mjjmax_selection = event.selectors['mjjmax'].selections
    #    if maxpt_selection == mjjmax_selection: num_same += 1

    #print(num_same, index, num_same/index)



print_event('sig')
print()
print_event('bgd')
