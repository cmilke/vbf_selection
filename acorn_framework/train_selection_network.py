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

    prepared_data = []
    data_labels = []
    for event in data_dump[training_category].events:
        if len(event.jets) not in training_class.jet_count_range: continue
        prepared_event = training_class.prepare_event(event)
        prepared_data.append(prepared_event)

        label = training_class.get_label(event)
        data_labels.append(label)
        if len(prepared_data) >= 10: break
    if len(prepared_data) == 0: raise RuntimeError('Data List is Empty. Aborting!')

    training_cutoff = int( len(prepared_data)* (3/4) )
    #training_data   = prepared_data[:training_cutoff]
    #training_data   = numpy.array([prepared_data[0]])
    training_data   = prepared_data[:2]
    testing_data    = prepared_data[training_cutoff:]
    #training_labels = data_labels[:training_cutoff]
    training_labels = [ data_labels[:2] ]
    testing_labels  = data_labels[training_cutoff:]

    training_class.train_model(training_data, training_labels)
    training_class.test_model(testing_data, testing_labels)


train()
