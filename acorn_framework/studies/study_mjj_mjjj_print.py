#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

_category_key = 'JVT'
_selector_key = 'mjjmax'
_efficiency_cuts = {
    0.4: (660, 810)
  , 0.6: (450, 566)
  , 0.8: (300, 390)
}


def print_event_relation(input_type):
    # 0 = no match, 1 = matching
    relation_counts = {
        0.4: [0]*2
      , 0.6: [0]*2
      , 0.8: [0]*2
    }

    data_dump = pickle.load( open('data/output_'+input_type+'.p', 'rb') )
    event_index = 0
    for event in data_dump[_category_key].events:
        #if event_index >= 10: break
        if len(event.jets) != 3: continue
        event_index += 1

        selector = event.selectors[_selector_key]
        mjj = event.selectors[_selector_key].taggers['mjj'].discriminant
        mjjj = event.selectors[_selector_key].taggers['mjjj'].discriminant
        event_weight = event.event_weight
        for eff_level, (mjj_cut, mjjj_cut) in _efficiency_cuts.items():
            mjj_passed = int( mjj_cut < mjj)
            mjjj_passed = int( mjjj_cut < mjjj)
            matching = (mjj_passed + mjjj_passed + 1) % 2
            relation_counts[eff_level][matching] += 1
    print('total: ' + str(event_index) )
    print()
    for item in relation_counts.items(): print(item)



print_event_relation('sig')
#print_event_relation('bgd')
