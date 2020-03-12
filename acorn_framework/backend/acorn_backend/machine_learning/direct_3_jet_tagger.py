import numpy
import math
import tensorflow
import keras
from uproot_methods import TLorentzVector
from acorn_backend.machine_learning.ML_tagger_base import ML_tagger_base

class direct_3_jet_tagger(ML_tagger_base):
    input_keys = ['E', 'pt', 'eta', 'phi', 'Deta', 'mjj']


    def __init__(self, key, tag=True):
        self.model_file = 'data/'+self.__class__.__name__+'.h5'
        if tag: self.network_model = keras.models.load_model(self.model_file)
        self.key = key


    def prepare_events(self, event_list, label_list):
        organized_data = { key:[] for key in self.input_keys }

        for event in event_list:
            E_list = []
            pt_list = []
            eta_list = []
            phi_list = []
            Deta_list = []
            mjj_list = []

            total_vector = TLorentzVector(0,0,0,0)
            for jet_index, jet in enumerate(event.jets):
                vec = jet.vector()
                E_list.append  ( vec.energy )
                pt_list.append ( jet.pt()  )
                eta_list.append( jet.eta() )
                phi_list.append( jet.phi() )
                for other_jet in event.jets[jet_index+1:]:
                    other_vec = other_jet.vector()
                    Deta = abs( jet.eta() - other_jet.eta() )
                    mjj = ( vec + other_jet.vector() ).mass
                    Deta_list.append(Deta)
                    mjj_list.append(mjj)
                total_vector += vec
            mjj_list.append( total_vector.mass )


            organized_data['E'].append( E_list )
            organized_data['pt'].append( pt_list )
            organized_data['eta'].append( eta_list )
            organized_data['phi'].append( phi_list )
            organized_data['Deta'].append( Deta_list )
            organized_data['mjj'].append( mjj_list )

            if label_list != None: label_list.append( self.get_label(event) )

        prepared_data = { key:numpy.array(val) for key,val in organized_data.items() }
        return prepared_data


    def train_model(self, training_data, training_labels):
        print('TRAINING NEW MODEL')

        input_list = [ keras.Input(shape=(3,), name=key) for key in self.input_keys[:-1] ]
        input_list.append( keras.Input(shape=(4,), name='mjj') )

        # Seperately allow network to process energies, pts, etas, etc...
        tensor_list = []
        output_list = []
        for nn_input in input_list:
            nn_tensor = keras.layers.Dense(12, activation="relu")(nn_input)
            nn_tensor = keras.layers.Dense(24, activation="relu")(nn_tensor)
            nn_tensor = keras.layers.Dense(25, activation="relu")(nn_tensor)
            sub_model = keras.Model(inputs=nn_input, outputs=nn_tensor)

            tensor_list.append(sub_model)
            output_list.append(sub_model.output)
         
        # Join all the individual models together
        united_outputs = output_list
        united_input = keras.layers.Concatenate(axis=1)(united_outputs)
        united_tensor = keras.layers.Dense(75, activation="relu")(united_input)
        united_tensor = keras.layers.Dense(70, activation="relu")(united_tensor)
        united_tensor = keras.layers.Dense(2, activation="softmax")(united_tensor)
         
        # Our model will accept the inputs of the five branches and then output 3 values
        united_inputs = input_list
        model = keras.Model(inputs=united_inputs, outputs=united_tensor)
        model.compile( optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        model.fit(x=training_data, y=training_labels, epochs=20) # Train Model
        model.save(self.model_file) # Save Model
