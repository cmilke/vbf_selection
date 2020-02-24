tensorflow = None
keras = None
Input = None
Dense = None
Model = None
run_mode = None

def load_tensorflow(mode):
    global tensorflow, keras
    global Input, Dense, Model, run_mode
    import tensorflow
    #from tensorflow import keras
    import keras
    from keras.layers import Input, Dense
    from keras.models import Model
    run_mode = mode
