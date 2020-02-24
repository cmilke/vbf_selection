import numpy
import math
from uproot_methods import TLorentzVector
import itertools

import acorn_backend.machine_learning.tensorflow_buffer as tb
from acorn_backend.machine_learning.simple_2_jet_tagger import simple_2_jet_tagger

class direct_3_jet_taggerV3(simple_2_jet_tagger):
    #############################################
    ### Neural Network specific class members ###
    #############################################
    model_file = 'data/direct_3_jet_taggerV3_model.h5'
    network_model = None

    @classmethod
    def prepare_events(cls, event_selections_tuple_list, label_list):
        organized_data = []

        for event, selections in event_selections_tuple_list:
            # Leading and Sub-leading invariant masses
            mass_pairs = [ (jet_i.vector+jet_j.vector).mass for jet_i,jet_j in itertools.combinations(event.jets, 2) ]
            mass_pairs.sort(reverse=True)

            # Forward Jet Centrality
            eta_sorted_jets = sorted(event.jets, key=lambda j: j.vector.eta)
            extra_Deta = eta_sorted_jets[1].vector.eta - eta_sorted_jets[0].vector.eta
            primary_Deta = eta_sorted_jets[2].vector.eta - eta_sorted_jets[0].vector.eta
            centrality = abs(2*extra_Deta / primary_Deta - 1)

            event_data = mass_pairs[:2] + [centrality]
            organized_data.append(event_data)
            if label_list != None: label_list.append( cls.get_label(event) )

        prepared_data = numpy.array(organized_data)
        return prepared_data


    @classmethod
    def train_model(cls, training_data, training_labels):
        print('TRAINING NEW MODEL')

        nn_input = tb.Input(shape=(3,))
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
    key = '3jNNtaggerV3'
    value_range = (-20, 20)
