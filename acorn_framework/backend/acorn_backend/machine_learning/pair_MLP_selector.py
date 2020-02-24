import acorn_backend.machine_learning.tensorflow_buffer as tb
from acorn_backend.machine_learning.basic_neural_net_selector import basic_neural_net_selector

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
    def prepare_events(cls, event_list, label_list):
        organized_data = { 'pair0':[],'pair1':[],'pair2':[] }
        for event in event_list:
            vecs = [ jet.vector for jet in event.jets ]
            organized_data['pair0'].append( cls.getpair(vecs[0], vecs[1]) )
            organized_data['pair1'].append( cls.getpair(vecs[0], vecs[2]) )
            organized_data['pair2'].append( cls.getpair(vecs[1], vecs[2]) )

            if label_list != None: label_list.append( cls.get_label(event) )

        prepared_data = {}
        for key,val in organized_data.items(): prepared_data[key] = numpy.array(val)
        return prepared_data


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
