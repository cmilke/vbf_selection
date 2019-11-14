#!/usr/bin/env python

import sys
import math
import pickle
import numpy
import random
from acorn_backend.machine_learning import tensorflow_buffer
from acorn_backend.machine_learning.simple_2_jet_tagger import basic_nn_tagger as training_class
tensorflow_buffer.load_tensorflow()


def train():
    input_type = 'sig'
    training_category = 'JVT'
    training_selector = 'dummy2jet'

    # Randomly mix together signal and background events
    data_dump_sig = pickle.load( open('data/output_training_sig.p', 'rb') )
    data_dump_bgd = pickle.load( open('data/output_training_bgd.p', 'rb') )
    event_list = data_dump_sig[training_category].events
    event_list += data_dump_bgd[training_category].events
    random.shuffle(event_list)

    prepared_data_list = []
    data_labels_list = []
    for event in event_list:
        if training_selector not in event.selectors: continue
        selections = event.selectors[training_selector].selections
        prepared_event = training_class.prepare_event(event,selections)
        prepared_data_list.append(prepared_event)

        label = training_class.get_label(event)
        data_labels_list.append(label)
        #if len(prepared_data_list) >= 1000: break
    prepared_data = numpy.array(prepared_data_list)
    data_labels = numpy.array(data_labels_list)

    training_cutoff = int( len(prepared_data)* (3/4) )
    training_data   = prepared_data[:training_cutoff]
    testing_data    = prepared_data[training_cutoff:]
    training_labels = data_labels[:training_cutoff]
    testing_labels  = data_labels[training_cutoff:]

    training_class.train_model(training_data, training_labels)
    training_class.test_model(testing_data, testing_labels)


train()
