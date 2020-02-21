#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import pickle
from itertools import combinations



def check_if_signature_jets(jets):
    for jet in jets:
        if not jet.is_truth_quark(): return False
    return True


def draw(input_type):
    data_dump = pickle.load( open('data/output_aviv_record_'+input_type+'.p', 'rb') )

    events_with_3_jets = [ event for event in data_dump['JVT'].events if len(event.jets) == 3 ][:int(1e6)]
    correct_pt = 0
    correct_mjj = 0
    tagged_pt = 0
    tagged_mjj = 0
    for event in events_with_3_jets:
        # Leading Pt
        pt_ordered_jets = sorted(event.jets, key=lambda j: j.vector.pt, reverse=True)
        pt_chosen_jets = pt_ordered_jets[:2]
        if input_type == 'sig':
            correct_jets = check_if_signature_jets(pt_chosen_jets)
            correct_pt += int(correct_jets)

        tagged_pt += int( (pt_chosen_jets[0].vector + pt_chosen_jets[1].vector).mass > 252 )
        
        
        # Maximized Mjj
        mass_pairs = sorted( [ ( (i.vector+j.vector).mass, [i,j] ) for i,j in combinations(event.jets, 2) ], reverse=True, key=lambda t: t[0])
        mjj_chosen_jets = mass_pairs[0][1]
        if input_type == 'sig':
            correct_jets = check_if_signature_jets(mjj_chosen_jets)
            correct_mjj += int(correct_jets)

        tagged_mjj += int( (mjj_chosen_jets[0].vector + mjj_chosen_jets[1].vector).mass > 310 )

    num_jets = len(events_with_3_jets)
    print(num_jets)
    if input_type == 'sig': print('{}, {}, {:.02}, {:.02}'.format(correct_pt, correct_mjj, correct_pt/num_jets, correct_mjj/num_jets) )
    print('{}, {}, {:.02}, {:.02}'.format(tagged_pt, tagged_mjj, tagged_pt/num_jets, tagged_mjj/num_jets) )

        

draw('sig')
print()
draw('bgd')
