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

    is_valid = lambda event: len(event.jets) in training_class.jet_count_range
    event_list = [ event for event in data_dump[training_category].events if is_valid(event) ]
    training_cutoff = int( len(event_list)*(3/4) )

    training_labels, testing_labels = [], []
    training_data = training_class.prepare_events(event_list[:training_cutoff], training_labels)
    testing_data = training_class.prepare_events(event_list[training_cutoff:], testing_labels)

    if len(training_labels) == 0: raise RuntimeError('Data List is Empty. Aborting!')
    training_class.train_model(training_data, training_labels)
    training_class.test_model(testing_data, testing_labels)


train()
