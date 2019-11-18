import acorn_backend.machine_learning.tensorflow_buffer as tb
from acorn_backend.machine_learning.basic_selector import basic_neural_net_selector

#Helper libraries
import numpy
import math
import matplotlib
import matplotlib.pyplot as plot
import acorn_backend.base_jet_selectors
from uproot_methods import TLorentzVector

class dual_layer_selector(basic_neural_net_selector):
    #############################################
    ### Neural Network specific class members ###
    #############################################
    model_file = 'data/dual_layer_selector_model.h5'
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
        m01 = (event.jets[0].vector + event.jets[1].vector).mass
        m02 = (event.jets[0].vector + event.jets[2].vector).mass
        m12 = (event.jets[1].vector + event.jets[2].vector).mass
        p_list.append([m01, m02, m12])
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
            tb.keras.layers.Flatten( input_shape=(4,3) ),
            tb.keras.layers.Dense(18, activation=tb.tensorflow.nn.relu),
            tb.keras.layers.Dense(30, activation=tb.tensorflow.nn.relu),
            tb.keras.layers.Dense(len(cls.pair_labels), activation=tb.tensorflow.nn.softmax)
        ])

        model.compile( optimizer='adam',
                       loss='sparse_categorical_crossentropy',
                       metrics=['accuracy'])

        model.fit(training_data, training_labels, epochs=7) # Train Model
        model.save(cls.model_file) # Save Model


    #############################
    ### Jet Selection Members ###
    #############################
    key = 'dualLayerNN'
