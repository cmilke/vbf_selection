#!/usr/bin/env python

import sys
import math
import pickle
import numpy
import random
from acorn_backend.machine_learning import tensorflow_buffer
from acorn_backend.machine_learning.direct_3_jet_taggerV3 import direct_3_jet_taggerV3 as training_class
tensorflow_buffer.load_tensorflow()


def train():
    training_category = 'JVT'
    training_selector = 'dummy3jet'

    # Randomly mix together signal and background events
    data_dump_sig = pickle.load( open('data/output_'+sys.argv[1]+'_train_sig.p', 'rb') )
    data_dump_bgd = pickle.load( open('data/output_'+sys.argv[1]+'_train_bgd.p', 'rb') )
    event_count = 40000
    event_list = data_dump_sig[training_category].events[:event_count]
    event_list += data_dump_bgd[training_category].events[:event_count]
    random.shuffle(event_list)

    # Collect events and associated selections
    make_input = lambda event: (event, event.selectors[training_selector].selections)
    input_list = [ make_input(event) for event in event_list if training_selector in event.selectors ]
    training_cutoff = int( len(input_list)* (3/4) )

    training_labels, testing_labels = [], []
    training_data = training_class.prepare_events(input_list[:training_cutoff], training_labels)
    testing_data = training_class.prepare_events(input_list[training_cutoff:], testing_labels)
    print(training_data)

    if len(training_labels) == 0: raise RuntimeError('Data List is Empty. Aborting!')
    training_class.train_model(training_data, training_labels)
    training_class.test_model(testing_data, testing_labels)


train()
