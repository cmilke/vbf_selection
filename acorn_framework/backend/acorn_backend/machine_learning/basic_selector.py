import numpy
import math
import acorn_backend.base_jet_selectors
import acorn_backend.machine_learning.tensorflow_buffer as tb
from uproot_methods import TLorentzVector
from acorn_backend.machine_learning.neural_network_template import template_NN

class basic_neural_net_selector(acorn_backend.base_jet_selectors.base_selector, template_NN):
    #############################################
    ### Neural Network specific class members ###
    #############################################
    model_file = 'data/basic_neural_net_selector_model.h5'
    jet_count_range = range(3,4) # This neural net is only intented for 3-jet events
    pair_labels = [
        [0,1],
        [0,2],
        [1,2]
    ]
    network_model = None
            

    @classmethod
    def prepare_event(cls, event):
        p_list = []
        for jet in event.jets:
            p_list.append([ jet.vector.p3.x, jet.vector.p3.y, jet.vector.p3.z ])
        prepared_event = numpy.array(p_list)
        return prepared_event


    @classmethod
    def get_label(cls, event):
        vbf_jets = [ i for i,jet in enumerate(event.jets) if jet.is_truth_quark() ]
        label = cls.pair_labels.index(vbf_jets)
        return label


    @classmethod
    def train_model(cls, training_data, training_labels):
        print('TRAINING NEW MODEL')

        # Build and compile neural network model 
        model = tb.keras.Sequential([
            tb.keras.layers.Flatten( input_shape=(3,3) ),
            tb.keras.layers.Dense(18, activation=tb.tensorflow.nn.relu),
            tb.keras.layers.Dense(3, activation=tb.tensorflow.nn.softmax)
        ])

        model.compile( optimizer='adam',
                       loss='sparse_categorical_crossentropy',
                       metrics=['accuracy'])

        model.fit(training_data, training_labels, epochs=5) # Train Model
        model.save(cls.model_file) # Save Model


    #############################
    ### Jet Selection Members ###
    #############################
    key = 'basicNN'

    def select(self, event):
        cls = self.__class__
        if cls.network_model == None:
            return (0,1)
        else:
            prepared_event = cls.prepare_event(event)
            singular_datum = numpy.array([prepared_event])
            predictions = cls.network_model.predict(singular_datum)[0]
            prediction_index = numpy.argmax(predictions)
            jet_index_pair = cls.pair_labels[prediction_index]
            return tuple(jet_index_pair)
