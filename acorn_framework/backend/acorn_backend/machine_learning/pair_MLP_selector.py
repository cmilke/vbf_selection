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
    pair_labels = [
        [0,1],
        [0,2],
        [1,2]
    ]
    network_model = None

    getpair = lambda a,b: [abs(a.eta-b.eta), (a+b).mass]
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
    def get_label(cls, event):
        vbf_jets = [ i for i,jet in enumerate(event.jets) if jet.is_truth_quark() ]
        label = cls.pair_labels.index(vbf_jets)
        return label


    @classmethod
    def train_model(cls, unmerged_training_data, training_labels):
        print('TRAINING NEW MODEL')

        training_data = unmerged_training_data
        #training_data = { 'pair0':[],'pair1':[],'pair2':[],'pt_list':[],'eta_list':[] }
        #for data_dict in unmerged_training_data:
        #    for key, val in data_dict.items():
        #        training_data[key].append(val)
        #    
        #for key, val in training_data.items():
        #    training_data[key] = numpy.array( training_data[key] )

        pair_input_list = [ tb.Input(shape=(2,), name='pair'+str(i)) for i in range(3) ]
        pt_input  = tb.Input(shape=(3,), name='pt_list')
        eta_input = tb.Input(shape=(3,), name='eta_list')

        pair_tensor_list = []
        pair_output_list = []
        for pairinput in pair_input_list:
            pair_tensor = tb.Dense(8, activation="relu")(pairinput)
            pair_tensor = tb.Dense(4, activation="relu")(pair_tensor)
            pair_tensor = tb.Model(inputs=pairinput, outputs=pair_tensor)
            pair_tensor_list.append(pair_tensor)
            pair_output_list.append(pair_tensor.output)
         
        pt_tensor = tb.Dense(18, activation="relu")(pt_input)
        pt_tensor = tb.Dense(4, activation="relu")(pt_tensor)
        pt_tensor = tb.Model(inputs=pt_input, outputs=pt_tensor)

        eta_tensor = tb.Dense(18, activation="relu")(eta_input)
        eta_tensor = tb.Dense(4, activation="relu")(eta_tensor)
        eta_tensor = tb.Model(inputs=eta_input, outputs=eta_tensor)
         

        # Join all 3 pair tensors with the pt and eta tensors
        united_outputs = pair_output_list + [pt_tensor.output, eta_tensor.output] 
        united_input = tb.keras.layers.Concatenate(axis=1)(united_outputs)
        united_tensor = tb.Dense(5, activation="relu")(united_input)
        united_tensor = tb.Dense(len(cls.pair_labels), activation="softmax")(united_tensor)
         
        # Our model will accept the inputs of the five branches and then output 3 values
        united_inputs = pair_input_list + [pt_input, eta_input]
        model = tb.Model(inputs=united_inputs, outputs=united_tensor)


        model.compile( optimizer='adam',
                       loss='sparse_categorical_crossentropy',
                       metrics=['accuracy'])

        model.fit(x=training_data, y=training_labels, epochs=7) # Train Model
        model.save(cls.model_file) # Save Model


    #############################
    ### Jet Selection Members ###
    #############################
    key = 'pairMLP'
