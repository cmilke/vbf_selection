#!/usr/bin/env python
import sys
import math
import pickle
import numpy
import random

from acorn_backend.tagger_methods import selector_options
from acorn_backend.tagger_methods import jet_ident_counter
from acorn_backend.machine_learning.ML_tagger_base import ML_tagger_base
from acorn_backend.machine_learning.direct_3_jet_tagger import direct_3_jet_tagger

def train():
    training_category = 'JVT_50-30'
    #tagger_to_train = ML_tagger_base('', selector_options['all'], tag=False)
    tagger_to_train = direct_3_jet_tagger('', tag=False)

    # Randomly mix together signal and background events
    data_dump_sig = pickle.load( open('data/output_'+sys.argv[1]+'_train_sig.p', 'rb') )
    data_dump_bgd = pickle.load( open('data/output_'+sys.argv[1]+'_train_bgd.p', 'rb') )
    event_count = 30000
    #valid = jet_ident_counter['2jet']
    valid = jet_ident_counter['>=3jet']
    sig_list = [ event for event in data_dump_sig[training_category].events if valid(event) ][:event_count]
    bgd_list = [ event for event in data_dump_bgd[training_category].events if valid(event) ][:event_count]
    print(len(sig_list), len(bgd_list))
    event_list = sig_list + bgd_list

    random.seed(768234)
    random.shuffle(event_list)
    training_cutoff = int( len(event_list)* (3/4) )
    training_labels, testing_labels = [], []
    training_data = tagger_to_train.prepare_events(event_list[:training_cutoff], training_labels)
    testing_data = tagger_to_train.prepare_events(event_list[training_cutoff:], testing_labels)
    print(training_data)

    if len(training_labels) == 0: raise RuntimeError('Data List is Empty. Aborting!')
    tagger_to_train.train_model(training_data, training_labels)
    tagger_to_train.test_model(testing_data, testing_labels)


train()
