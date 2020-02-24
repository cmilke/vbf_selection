import numpy
import math
from uproot_methods import TLorentzVector

import acorn_backend.machine_learning.tensorflow_buffer as tb
from acorn_backend.machine_learning.simple_2_jet_tagger import simple_2_jet_tagger

class direct_3_jet_tagger(simple_2_jet_tagger):
    #############################################
    ### Neural Network specific class members ###
    #############################################
    model_file = 'data/direct_3_jet_tagger_model.h5'
    network_model = None

    input_keys = ['E', 'pt', 'eta', 'phi', 'Deta', 'mjj']

    @classmethod
    def prepare_events(cls, event_selections_tuple_list, label_list):
        organized_data = { key:[] for key in cls.input_keys }

        for event, selections in event_selections_tuple_list:
            E_list = []
            pt_list = []
            eta_list = []
            phi_list = []
            Deta_list = []
            mjj_list = []

            total_vector = TLorentzVector(0,0,0,0)
            for jet_index, jet in enumerate(event.jets):
                E_list.append  ( jet.vector.energy )
                pt_list.append ( jet.vector.pt     )
                eta_list.append( jet.vector.eta    )
                phi_list.append( jet.vector.phi    )
                for other_jet in event.jets[jet_index+1:]:
                    Deta = abs( jet.vector.eta - other_jet.vector.eta )
                    mjj = ( jet.vector + other_jet.vector ).mass
                    Deta_list.append(Deta)
                    mjj_list.append(mjj)
                total_vector += jet.vector
            mjj_list.append( total_vector.mass )


            organized_data['E'].append( E_list )
            organized_data['pt'].append( pt_list )
            organized_data['eta'].append( eta_list )
            organized_data['phi'].append( phi_list )
            organized_data['Deta'].append( Deta_list )
            organized_data['mjj'].append( mjj_list )

            if label_list != None: label_list.append( cls.get_label(event) )

        prepared_data = { key:numpy.array(val) for key,val in organized_data.items() }
        return prepared_data


    @classmethod
    def train_model(cls, training_data, training_labels):
        print('TRAINING NEW MODEL')

        input_list = [ tb.Input(shape=(3,), name=key) for key in cls.input_keys[:-1] ]
        input_list.append( tb.Input(shape=(4,), name='mjj') )

        # Seperately allow network to process energies, pts, etas, etc...
        tensor_list = []
        output_list = []
        for nn_input in input_list:
            nn_tensor = tb.Dense(12, activation="relu")(nn_input)
            nn_tensor = tb.Dense(24, activation="relu")(nn_tensor)
            nn_tensor = tb.Dense(25, activation="relu")(nn_tensor)
            sub_model = tb.Model(inputs=nn_input, outputs=nn_tensor)

            tensor_list.append(sub_model)
            output_list.append(sub_model.output)
         
        # Join all the individual models together
        united_outputs = output_list
        united_input = tb.keras.layers.Concatenate(axis=1)(united_outputs)
        united_tensor = tb.Dense(75, activation="relu")(united_input)
        united_tensor = tb.Dense(70, activation="relu")(united_tensor)
        united_tensor = tb.Dense(2, activation="softmax")(united_tensor)
         
        # Our model will accept the inputs of the five branches and then output 3 values
        united_inputs = input_list
        model = tb.Model(inputs=united_inputs, outputs=united_tensor)
        model.compile( optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        model.fit(x=training_data, y=training_labels, epochs=20) # Train Model
        model.save(cls.model_file) # Save Model


    ######################
    ### Tagger Members ###
    ######################
    key = '3jNNtagger'
    value_range = (-20, 20)
