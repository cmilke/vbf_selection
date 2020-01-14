#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import pickle
    

def draw(input_type):
    data_dump = pickle.load( open('data/output_untagged_'+input_type+'.p', 'rb') )

    # Yes, this is a silly way to do this, but I was having fun. If you can't follow it, just rewrite it from scratch. It should only take you 5 min.

    events_with_3_jets = [ event for event in data_dump['JVT'].events if len(event.jets) == 3 ]
    # Number of 3-jet events with at least 1 pileup jet
    print(  [ True in [jet.is_pileup for jet in event.jets] for event in events_with_3_jets ].count(True) / len(events_with_3_jets)  )

    # Number of 3-jet events where a pileup jet is the lowest pt jet
    print(  [ sorted(event.jets,key=lambda j: j.vector.pt)[0].is_pileup for event in events_with_3_jets ].count(True) / len(events_with_3_jets) )

draw('sig')
print()
draw('bgd')
