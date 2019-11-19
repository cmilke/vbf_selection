#!/usr/bin/env python

import sys
import math
import pickle
import numpy
from acorn_backend.machine_learning import tensorflow_buffer
#from acorn_backend.machine_learning.basic_selector import basic_neural_net_selector as training_class
#from acorn_backend.machine_learning.dual_layer_selector import dual_layer_selector as training_class
from acorn_backend.machine_learning.pair_MLP_selector import pair_MLP_selector as training_class
tensorflow_buffer.load_tensorflow()


def train():
    input_type = 'sig'
    training_category = 'JVT'
    data_dump = pickle.load( open('data/output_training_'+input_type+'.p', 'rb') )

    event_list = []
    for event in data_dump[training_category].events:
        if len(event.jets) not in training_class.jet_count_range: continue
        event_list.append(event)
        #if len(event_list) >= 10: break

    training_cutoff = int( len(event_list)*(3/4) )
    training_data, training_labels = training_class.prepare_event_batch(event_list[:training_cutoff])
    testing_data, testing_labels = training_class.prepare_event_batch(event_list[training_cutoff:])
    if len(training_data) == 0: raise RuntimeError('Data List is Empty. Aborting!')

    training_class.train_model(training_data, training_labels)
    training_class.test_model(testing_data, testing_labels)


train()
