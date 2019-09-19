from __future__ import absolute_import, division, print_function
import sys

#TensorFlor and tf.keras
import tensorflow
from tensorflow import keras

#Helper libraries
import numpy
import matplotlib
import matplotlib.pyplot as plot




def train_model(rescaled_train_images, train_labels):
    print('TRAINING NEW MODEL')
    #########################################
    #Build and compile neural network model 
    #########################################
    model = keras.Sequential([
        keras.layers.Flatten( input_shape=(28,28) ),
        keras.layers.Dense(128, activation=tensorflow.nn.relu),
        keras.layers.Dense(10, activation=tensorflow.nn.softmax)
    ])


    model.compile( optimizer='adam',
                   loss='sparse_categorical_crossentropy',
                   metrics=['accuracy'])


    #########################################
    ### Train Model
    #########################################
    model.fit(rescaled_train_images, train_labels, epochs=5)


    #########################################
    ### Save Model
    #########################################
    model.save('tutorial_fashion_model.h5')


def test_model(rescaled_test_images, test_labels):
    print('TESTING MODEL')
    #########################################
    ### Load Model
    #########################################
    model = keras.models.load_model('tutorial_fashion_model.h5')


    #########################################
    ### Evaluate Trained Model
    #########################################
    test_loss, test_accuracy = model.evaluate(rescaled_test_images, test_labels)
    print('Test accuracy: ', test_accuracy)

    predictions = model.predict(rescaled_test_images)

    print(predictions[0])


############
#load data#
############
fashion_mnist = keras.datasets.fashion_mnist

(train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()
class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']


#print( train_images.shape )
#print( len(train_labels) )

#plot.figure()
#plot.imshow(train_images[0])
#plot.colorbar()
#plot.grid(False)
#plot.show()

###############
#prepare data
###############
rescaled_train_images = train_images / 255.0
rescaled_test_images = test_images / 255.0

#plot.figure(figsize=(10,10))
#for i in range(25):
#    plot.subplot(5,5,i+1)
#    plot.xticks([])
#    plot.yticks([])
#    plot.grid(False)
#    plot.imshow(rescaled_train_images[i], cmap=plot.cm.binary)
#    plot.xlabel(class_names[train_labels[i]])
#plot.show()

if sys.argv[1] == 'train':
    train_model(rescaled_train_images, train_labels)
else:
    test_model(rescaled_test_images, test_labels)
    
