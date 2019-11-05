#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

_category_key = 'JVT'


def print_event_relation(input_type):
    # 0 = no match, 1 = matching
    relation_counts = [0,0]

    data_dump = pickle.load( open('data/output_'+input_type+'.p', 'rb') )
    event_index = 0
    for event in data_dump[_category_key].events:
        #if event_index >= 10: break
        if len(event.jets) != 3: continue
        event_index += 1

        etamax_selections = event.selectors['etamax'].selections
        mjjmax_selections = event.selectors['mjjmax'].selections
        matched0 = etamax_selections[0] in mjjmax_selections
        matched1 = etamax_selections[1] in mjjmax_selections
        matching = int( matched0 and matched1 )
        relation_counts[matching] += 1
    print('total: ' + str(event_index) )
    print(relation_counts)



print_event_relation('sig')
#print_event_relation('bgd')
