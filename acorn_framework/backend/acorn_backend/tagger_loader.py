import acorn_backend.base_jet_selectors as base_selectors

from acorn_backend.machine_learning import tensorflow_buffer
from acorn_backend.machine_learning.basic_selector import basic_neural_net_selector
from acorn_backend.machine_learning.dual_layer_selector import dual_layer_selector
from acorn_backend.machine_learning.pair_MLP_selector import pair_MLP_selector
from acorn_backend.machine_learning.simple_2_jet_tagger import basic_nn_tagger
from acorn_backend.machine_learning.direct_3_jet_tagger import direct_3_jet_tagger

selector_options = [
    [], #0
    [], #1
    [ #2
        base_selectors.base_selector
      #, base_selectors.dummy_2_jet_selector
    ],
    [ #3
        base_selectors.truth_selector
      , base_selectors.maximal_mjj_selector
      , base_selectors.highest_pt_selector
      , base_selectors.random_selector
      , base_selectors.maximal_Delta_eta_selector
      #, base_selectors.quark_gluon_tag_selector
      #, base_selectors.coLinearity_merger
      , base_selectors.dummy_3_jet_selector
      #, basic_neural_net_selector 
      #, dual_layer_selector 
      #, pair_MLP_selector
    ]
]


def load_network_models(mode):
    tensorflow_buffer.load_tensorflow()

    #basic_neural_net_selector.load_model(mode)
    #dual_layer_selector.load_model(mode)
    #pair_MLP_selector.load_model(mode)
    #basic_nn_tagger.load_model(mode)
    #direct_3_jet_tagger.load_model(mode)
