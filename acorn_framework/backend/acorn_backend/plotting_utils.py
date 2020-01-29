import pickle


Hist_bins = 200


# Used by the retrieve_data function to deal with the intricacies of 
# dumping valies into the data map
def fill_event_map(event_map, event_key, tagger, event_weight):
    discriminant = tagger.discriminant
    value_range = tagger.__class__.value_range

    if discriminant < value_range[0]:
        discriminant = value_range[0]
    if discriminant > value_range[1]:
        discriminant = value_range[1] - (value_range[1] - value_range[0])/Hist_bins

    if event_key not in event_map: event_map[event_key] = ( value_range, ([],[]) )
    event_map[event_key][1][0].append(discriminant)
    event_map[event_key][1][1].append(event_weight)


# Retrieves the nested data structure from the specified output file,
# and then restructures the data to be usuable for this analysis
def retrieve_data( input_type ):
    event_map = {}
    event_dump = pickle.load( open('data/output_aviv_tag_'+input_type+'.p', 'rb') )
    #event_dump = pickle.load( open('data/output_cmilkeV1_truth_tag_'+input_type+'.p', 'rb') )
    for category in event_dump.values():
        for event in category.events:
            jet_count = len(event.jets)
            event_weight = event.event_weight
            for selector in event.selectors.values():
                for tagger in selector.taggers.values():
                    event_key = (jet_count, category.key, selector.key, tagger.key)
                    fill_event_map(event_map, event_key, tagger, event_weight)
    return event_map


def accumulate_performance(distro, is_bgd):
        sum_direction = 1 if is_bgd else -1
        flip = slice(None,None,sum_direction)
        performance = distro[flip].cumsum()[flip]
        return performance
