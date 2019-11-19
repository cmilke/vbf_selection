import acorn_backend.machine_learning.tensorflow_buffer as tb
from acorn_backend.machine_learning.basic_selector import basic_neural_net_selector

#Helper libraries
import numpy
import math
import matplotlib
import matplotlib.pyplot as plot
import acorn_backend.base_jet_selectors
from uproot_methods import TLorentzVector

class pair_MLP_selector(basic_neural_net_selector):
    #############################################
    ### Neural Network specific class members ###
    #############################################
    model_file = 'data/pair_MLP_selector.h5'
    pair_labels = [ [0,1], [0,2], [1,2] ]
    network_model = None

    @classmethod
    def getpair(cls, vector1, vector2):
        jet_pair_feature_list = [
            (vector1+vector2).mass
          , vector1.energy
          , vector2.energy
          , vector1.pt
          , vector2.pt
          , vector1.eta
          , vector2.eta
          , vector1.phi
          , vector2.phi
        ]
        return jet_pair_feature_list


    @classmethod
    def prepare_event(cls, event):
        vecs = [ jet.vector for jet in event.jets ]

        prepared_event = {
            'pair0'   : numpy.array( cls.getpair(vecs[0], vecs[1]) )
          , 'pair1'   : numpy.array( cls.getpair(vecs[0], vecs[2]) )
          , 'pair2'   : numpy.array( cls.getpair(vecs[1], vecs[2]) )
          , 'pt_list' : numpy.array( [ v.pt for v in vecs ] )
          , 'eta_list': numpy.array( [ v.eta for v in vecs ] )
        }
        return prepared_event


    @classmethod
    def prepare_event_batch(cls, event_list):
        batch_data = { 'pair0':[],'pair1':[],'pair2':[] }
        data_labels = []
        for event in event_list:
            vecs = [ jet.vector for jet in event.jets ]
            batch_data['pair0'].append( cls.getpair(vecs[0], vecs[1]) )
            batch_data['pair1'].append( cls.getpair(vecs[0], vecs[2]) )
            batch_data['pair2'].append( cls.getpair(vecs[1], vecs[2]) )

            label = cls.get_label(event)
            data_labels.append(label)
        prepared_data = {}
        for key,val in batch_data.items(): prepared_data[key] = numpy.array(val)
        return prepared_data, data_labels


    @classmethod
    def get_label(cls, event):
        vbf_jets = [ i for i,jet in enumerate(event.jets) if jet.is_truth_quark() ]
        label = cls.pair_labels.index(vbf_jets)
        return label


    @classmethod
    def train_model(cls, training_data, training_labels):
        print('TRAINING NEW MODEL')

        pair_input_list = [ tb.Input(shape=(9,), name='pair'+str(i)) for i in range(3) ]

        pair_tensor_list = []
        pair_output_list = []
        for pair_input in pair_input_list:
            pair_tensor = tb.Dense(20, activation="relu")(pair_input)
            pair_tensor = tb.Dense(20, activation="relu")(pair_tensor)
            pair_tensor = tb.Dense(10, activation="relu")(pair_tensor)
            pair_tensor = tb.Model(inputs=pair_input, outputs=pair_tensor)
            pair_tensor_list.append(pair_tensor)
            pair_output_list.append(pair_tensor.output)
         
        # Join all 3 pair tensors with the pt and eta tensors
        united_outputs = pair_output_list
        united_input = tb.keras.layers.Concatenate(axis=1)(united_outputs)
        united_tensor = tb.Dense(60, activation="relu")(united_input)
        united_tensor = tb.Dense(20, activation="relu")(united_input)
        united_tensor = tb.Dense(len(cls.pair_labels), activation="softmax")(united_tensor)
         
        # Our model will accept the inputs of the five branches and then output 3 values
        united_inputs = pair_input_list
        model = tb.Model(inputs=united_inputs, outputs=united_tensor)
        model.compile( optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        model.fit(x=training_data, y=training_labels, epochs=20) # Train Model
        model.save(cls.model_file) # Save Model


    #############################
    ### Jet Selection Members ###
    #############################
    key = 'pairMLP'
