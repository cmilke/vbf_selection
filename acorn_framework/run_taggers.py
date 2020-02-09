#!/usr/bin/env python
import argparse
import pickle
from acorn_backend import analysis_utils as autils
from acorn_backend import categorization_classes
from acorn_backend.tagger_loader import load_network_models
from acorn_backend import ntuple_recording

#Define all the high level root stuff: ntuple files, branches to be used, etc.
# TODO: Can you have only one sample, that you only record once,
#   and then the tag/train samples are just limited slices of that pre-recorded sample
#   (since the tag method is now seperated from the recording method)
_ntuples_configuration = {
    'aviv': {
        'samples': {
            'sig': {
               'tag': autils.Flavntuple_list_VBFH125_gamgam[:2]
             , 'train': autils.Flavntuple_list_VBFH125_gamgam[4:6]
             , 'record': autils.Flavntuple_list_VBFH125_gamgam
            },
            'bgd': {
                'tag': autils.Flavntuple_list_ggH125_gamgam[:2]
              , 'train': autils.Flavntuple_list_ggH125_gamgam[7:9]
              , 'record': autils.Flavntuple_list_ggH125_gamgam
            }
        },
        'recorders': [
            ntuple_recording.record_aviv_reco_jets,
            ntuple_recording.record_aviv_truth_jets
        ]
    },

    'cmilkeV1': {
        'tree_name': 'ntuple',
        'samples': {
            'sig': {
               'tag': autils.Flavntuple_list_VBFH125_gamgam_V2
             , 'train': None 
             , 'record': autils.Flavntuple_list_VBFH125_gamgam_V2
            },
            'bgd': {
                'tag': autils.Flavntuple_list_ggH125_gamgam_V2
              , 'train': None
              , 'record': autils.Flavntuple_list_ggH125_gamgam_V2
            }
        },
        'recorders': [
            ntuple_recording.record_cmilkeV1_reco_jets,
            ntuple_recording.record_cmilkeV1_truth_jets
        ]
    },

    'data': None
}

_categories_to_dump = [
    #categorization_classes.filter_with_JVTmin20,
    categorization_classes.filter_with_JVT
]

_Nevents_debug_default = 10


def record_events(input_type, args):
    # Apply commandline arguments
    record_jets = _ntuples_configuration[args.ntuple]['recorders'][args.t]
    input_list = _ntuples_configuration[args.ntuple]['samples'][input_type][args.mode]
    events_to_read = _Nevents_debug_default if (args.debug and args.Nevents == None) else args.Nevents

    # Define and initialize all event categories we want to use
    event_data_dump = { c.key: c() for c in _categories_to_dump }

    # Iterate over each event in the ntuple list,
    # storing/sorting/filtering events into the data_dump as it goes
    record_jets(input_type == 'sig', input_list, events_to_read, event_data_dump)

    if args.mode != 'record':
        print('Tagging Events Now!')
        for category in event_data_dump.values(): category.tag_events()


    # Print out either the full debug information, or just a summary
    for category in event_data_dump.values():
        print( category if args.debug else category.summary() )

    # Output the event categories for use by later scripts
    reco_level = '_truth' if args.t else ''
    data_dump_file_name = 'data/output_'+args.ntuple+reco_level+'_'+args.mode+'_'+input_type+'.p'
    pickle.dump( event_data_dump, open(data_dump_file_name, 'wb') )


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", required = False,
        default = False, action = 'store_true',
        help = "Run over Signal events",
    ) 
    parser.add_argument(
        "-b", required = False,
        default = False, action = 'store_true',
        help = "Run over Background events"
            "(Note: if neither -s or -b are given, default behaviour is to run over both)",
    ) 
    parser.add_argument(
        "--Nevents", required = False,
        default = None, type=int,
        help     = "How many events you want to run over",
    ) 
    parser.add_argument(
        "--mode", required = False,
        default = 'tag', type=str,
        help = "Modes: 'tag'    - Standard tagging procedure;"
               "       'train'  - Use training samples; keras models are permitted to fail on load;"
               "       'record' - Run over all samples, but merely categorize events, do not tag them",
    ) 
    parser.add_argument(
        "--ntuple", required = False,
        default = 'cmilkeV1', type=str,
        help = "Ntuples: 'aviv'      - Original ntuples from Aviv. Legacy based;"
               "         'cmilkeV1'  - Newer ntuples generated by Chris Milke with track info;"
               "         'data'      - Ntuples based on real data",
    ) 
    parser.add_argument(
        "--debug", required = False,
        default = False, action = 'store_true',
        help = "Prints debug information",
    ) 
    parser.add_argument(
        "-t", required = False,
        default = False, action = 'store_true',
        help = "Use truth jets instead of reco",
    ) 
    args = parser.parse_args()

    if args.mode != 'record': load_network_models(args.mode)
    if args.s: record_events('sig', args)
    if args.b: record_events('bgd', args)
    if not (args.b or args.s):
        record_events('sig', args)
        record_events('bgd', args)

run()
