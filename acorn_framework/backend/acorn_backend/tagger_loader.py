import acorn_backend.base_jet_selectors as base_selectors

from acorn_backend.machine_learning import tensorflow_buffer
from acorn_backend.machine_learning.basic_selector import basic_neural_net_selector
from acorn_backend.machine_learning.simple_2_jet_tagger import basic_nn_tagger

selector_options = [
    [], #0
    [], #1
    [ #2
        base_selectors.base_selector
      , base_selectors.dummy_2_jet_selector
    ],
    [ #3
        base_selectors.truth_selector
      , base_selectors.maximal_mjj_selector
      #, base_selectors.highest_pt_selector
      , base_selectors.random_selector
      , basic_neural_net_selector 
    ]
]


def load_network_models():
    tensorflow_buffer.load_tensorflow()

    basic_neural_net_selector.load_model()
    basic_nn_tagger.load_model()
