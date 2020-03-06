#!/usr/bin/env python
import sys
import math
import pickle
import numpy
import random

from acorn_backend.tagger_methods import selector_options
from acorn_backend.machine_learning.ML_tagger_base import ML_tagger_base

def train():
    training_category = 'JVT'
    tagger_to_train = ML_tagger_base(selector_options['all'], tag=False)

    # Randomly mix together signal and background events
    data_dump_sig = pickle.load( open('data/output_'+sys.argv[1]+'_train_sig.p', 'rb') )
    data_dump_bgd = pickle.load( open('data/output_'+sys.argv[1]+'_train_bgd.p', 'rb') )
    event_count = 40000
    event_list = data_dump_sig[training_category].events[:event_count]
    event_list += data_dump_bgd[training_category].events[:event_count]
    random.seed(768234)
    random.shuffle(event_list)

    # Collect events and associated selections
    valid_event = lambda event : len(event.jets) == 2
    input_list = [ event for event in event_list if valid_event(event) ]
    training_cutoff = int( len(input_list)* (3/4) )

    training_labels, testing_labels = [], []
    training_data = tagger_to_train.prepare_events(input_list[:training_cutoff], training_labels)
    testing_data = tagger_to_train.prepare_events(input_list[training_cutoff:], testing_labels)
    print(training_data)

    if len(training_labels) == 0: raise RuntimeError('Data List is Empty. Aborting!')
    tagger_to_train.train_model(training_data, training_labels)
    tagger_to_train.test_model(testing_data, testing_labels)


train()
