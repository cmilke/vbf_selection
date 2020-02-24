import numpy
import math
from uproot_methods import TLorentzVector
import itertools

import acorn_backend.machine_learning.tensorflow_buffer as tb
from acorn_backend.machine_learning.simple_2_jet_tagger import simple_2_jet_tagger

class direct_3_jet_taggerV2(simple_2_jet_tagger):
    #############################################
    ### Neural Network specific class members ###
    #############################################
    model_file = 'data/direct_3_jet_taggerV2_model.h5'
    network_model = None

    @classmethod
    def prepare_events(cls, event_selections_tuple_list, label_list):
        organized_data = []

        for event, selections in event_selections_tuple_list:
            #for data_list in organized_data.values: data_list.append([])
            mass_pairs = [ (jet_i.vector+jet_j.vector).mass for jet_i,jet_j in itertools.combinations(event.jets, 2) ]
            mass_pairs.sort(reverse=True)
            organized_data.append(mass_pairs[:2])
            if label_list != None: label_list.append( cls.get_label(event) )

        prepared_data = numpy.array(organized_data)
        return prepared_data


    @classmethod
    def train_model(cls, training_data, training_labels):
        print('TRAINING NEW MODEL')

        nn_input = tb.Input(shape=(2,))
        nn_tensor = tb.Dense(4, activation="relu")(nn_input)
        nn_tensor = tb.Dense(24, activation="relu")(nn_tensor)
        nn_tensor = tb.Dense(24, activation="relu")(nn_tensor)
        nn_tensor = tb.Dense(12, activation="relu")(nn_tensor)
        nn_tensor = tb.Dense(2, activation="softmax")(nn_tensor)

        model = tb.Model(inputs=nn_input, outputs=nn_tensor)
        model.compile( optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        model.fit(x=training_data, y=training_labels, epochs=20) # Train Model
        model.save(cls.model_file) # Save Model


    ######################
    ### Tagger Members ###
    ######################
    key = '3jNNtaggerV2'
    value_range = (-20, 20)
