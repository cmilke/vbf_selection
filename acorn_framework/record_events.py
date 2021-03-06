#!/usr/bin/env python
import argparse
import pickle
from acorn_backend import analysis_utils as autils
from acorn_backend import categorization_classes
from acorn_backend import ntuple_recording

#Define all the high level root stuff: ntuple files, branches to be used, etc.
# samples = [ signal, background ] - recorders = [ reco jets, truth jets ]
_ntuples_configuration = {
    'aviv': {
        'samples': [ autils.Flavntuple_list_VBFH125_gamgam, autils.Flavntuple_list_ggH125_gamgam ],
        'recorders': [ ntuple_recording.record_aviv_reco_jets, ntuple_recording.record_aviv_truth_jets ]
    },
    'cmilke': {
        'samples': [ autils.Flavntuple_list_VBFH125_gamgam_cmilke, autils.Flavntuple_list_ggH125_gamgam_cmilke ],
        'recorders': [ ntuple_recording.record_cmilke_reco_jets, ntuple_recording.record_cmilke_truth_jets ]
    },
    'data': None
}

_categories_to_dump = [
    categorization_classes.filter_with_JVT
  , categorization_classes.filter_with_JVT_50_30
  , categorization_classes.filter_with_JVT_70_50_30
  #, categorization_classes.filter_with_JVT20
]

_Nevents_debug_default = 10


def record_events(input_type, args):
    reco_level = '_truth' if args.t else ''
    events_to_read = _Nevents_debug_default if (args.debug and args.Nevents == None) else args.Nevents

    # Define and initialize all event categories we want to use
    event_data_dump = { c.key: c() for c in _categories_to_dump }

    # Iterate over each event in the ntuple list,
    # storing/sorting/filtering events into the data_dump as it goes
    record_jets = _ntuples_configuration[args.ntuple]['recorders'][args.t]
    input_list = _ntuples_configuration[args.ntuple]['samples'][input_type == 'bgd']
    record_jets(input_type == 'sig', input_list, events_to_read, event_data_dump)

    # Print out either the full debug information, or just a summary
    for category in event_data_dump.values():
        print( category if args.debug else category.summary() )

    # Output the event categories for use by later scripts
    print('\nEvents recorded, pickling now...')
    data_dump_file_name = 'data/output_'+args.ntuple+reco_level+'_record_'+input_type+'.p'
    pickle.dump( event_data_dump, open(data_dump_file_name, 'wb') )
    print('Finished '+input_type+'!\n')


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument( "-t", required = False, default = False, action = 'store_true', help = "Use truth jets instead of reco",) 
    parser.add_argument( "-s", required = False, default = False, action = 'store_true', help = "Run over Signal events",) 
    parser.add_argument( "-b", required = False, default = False, action = 'store_true', help = "Run over Background events"
            "(Note: if neither -s nor -b are given, default behaviour is to run over both)",
    ) 
    parser.add_argument( "--Nevents", required = False, default = None, type=int, help = "How many events you want to run over. Default is all available",) 
    parser.add_argument( "--ntuple", required = False, default = 'cmilke', type=str,
        help = "Ntuples: 'aviv'      - Original ntuples from Aviv. Legacy based;"
               "         'cmilke'    - Newer ntuples generated by Chris Milke with track info;"
               "         'data'      - Ntuples based on real data",
    ) 
    parser.add_argument( "--debug", required = False, default = False, action = 'store_true', help = "Prints debug information",) 
    args = parser.parse_args()

    if args.s: record_events('sig', args)
    if args.b: record_events('bgd', args)
    if not (args.b or args.s):
        record_events('sig', args)
        record_events('bgd', args)

run()
