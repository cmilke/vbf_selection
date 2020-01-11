#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import pickle
#import numpy


def count(input_type):
    print(input_type)
    data_dump = pickle.load( open('data/output_aviv_truth_record_'+input_type+'.p', 'rb') )
    event_counts = {}
    for event in data_dump['JVT'].events:
        pdgid_list = [ jet.truth_id for jet in event.jets ]
        pdgid_list.sort()
        named_ids = []
        for pdgid in pdgid_list:
            if   pdgid < 0: named_ids.append('?')
            elif pdgid in range(1,7): named_ids.append('Q')
            elif pdgid == 21: named_ids.append('g')
            else: named_ids.append('!')

        key = tuple(named_ids)
        if key in event_counts: event_counts[key] += 1
        else: event_counts[key] = 1
    sorted_counts = [ (count, key) for key, count in event_counts.items() ]
    sorted_counts.sort(reverse=True)
    for count, key in sorted_counts: print('{}: {}'.format(key, count))




count('sig')
print()
count('bgd')
