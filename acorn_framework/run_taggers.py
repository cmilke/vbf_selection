#!/usr/bin/env python
import argparse
import pickle
from acorn_backend.tagger_methods import tagger_options, selector_options, jet_ident_counter
from acorn_backend.machine_learning.ML_tagger_base import ML_tagger_base

_Nevents_debug_default = 10
_tag_fraction = 0.5


def perform_ML_tagging(event_data_dump):
    # Load available NN taggers
    tagger_dict = tagger_options
    ML_tagger_options = { key:{} for key in tagger_dict.keys() }
    ML_tagger_options['2jet']['NN'] = ML_tagger_base(selector_options['all'])
    #ML_tagger_options['>=3jet']['maxpt_NN'] = ML_tagger_base(selector_options['maxpt'])

    
    # Mass process events with Keras
    for category in event_data_dump.values():
        for jet_ident, available_ML_taggers in ML_tagger_optjons.items():
            event_list = [ event for event in category.events if valid_event(event) ]
            for tagger_key, ML_tagger in available_ML_taggers.items():
                ML_tagger.mass_process(tagger_key, event_list)


def tag_events(input_type, args):
    reco_level = '_truth' if args.t else ''
    events_to_read = _Nevents_debug_default if (args.debug and args.Nevents == None) else args.Nevents

    print('Opening recorded categories...')
    record_name = 'data/output_'+args.ntuple+reco_level+'_record_'+input_type+'.p'
    event_data_dump = pickle.load( open(record_name, 'rb') )
    for key, category in event_data_dump.items():
        print( 'Processing ' + key + '...' )
        tag_index = int( len(category.events)*_tag_fraction )
        deletion_slice = slice(None, tag_index) if args.T else slice(tag_index, None)
        del(category.events[deletion_slice])
        if events_to_read != None: del(category.events[events_to_read:])
        print( 'Tagging...' )
        category.tag_events(tagger_dict)
    print('Events tagged, processing with Neural Networks...')
    if not args.T: perform_ML_tagging(event_data_dump)

    # Print out either the full debug information, or just a summary
    for category in event_data_dump.values():
        print( category if args.debug else category.summary() )

    # Output the event categories for use by later scripts
    print('\nEvents recorded, pickling now...')
    mode = 'train' if args.T else 'tag'
    data_dump_file_name = 'data/output_'+args.ntuple+reco_level+'_'+mode+'_'+input_type+'.p'
    pickle.dump( event_data_dump, open(data_dump_file_name, 'wb') )
    print('Finished '+input_type+'!\n')


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument( "-t", required = False, default = False, action = 'store_true', help = "Use truth jets instead of reco",) 
    parser.add_argument( "-T", required = False, default = False, action = 'store_true', help = "Prepare training set",) 
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

    if args.s: tag_events('sig', args)
    if args.b: tag_events('bgd', args)
    if not (args.b or args.s):
        tag_events('sig', args)
        tag_events('bgd', args)

run()
