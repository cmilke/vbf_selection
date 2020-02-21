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
def retrieve_data( data_file ):
    event_map = {}
    event_dump = pickle.load( open(data_file, 'rb') )
    for category in event_dump.values():
        for event in category.events:
            jet_count = len(event.jets)
            event_weight = event.event_weight
            for selector in event.selectors.values():
                for deep_filter in selector.deep_filters.values():
                    for tagger in deep_filter.taggers.values():
                        event_key = (jet_count, category.key, selector.key, deep_filter.key, tagger.key)
                        fill_event_map(event_map, event_key, tagger, event_weight)
    return event_map


def accumulate_performance(distro, is_bgd):
        sum_direction = 1 if is_bgd else -1
        flip = slice(None,None,sum_direction)
        performance = distro[flip].cumsum()[flip]
        return performance


_category_titles = {
    'minimal': ' w/o JVT'
  , 'JVT': ''
  , 'JVT20': ' >20GeV'
}

_selector_titles = {
    'null'     : ''
  , 'truth'    : ': Harsh Truth'
  , 'mjjSL'    : ': $M_{jj-SL}$'
  , 'mjjmax'   : ': Max $M_{jj}$'
  , '2maxpt'   : ': Leading $p_t$'
  , 'dummy3jet': ''
  , 'random'   : ': Random'
  , 'pairMLP'  : ': pairMLP'
}

_deep_filter_titles = {
    'any': ''
  , 'mjj500': ', $M_{jj} > 500$ GeV'
}

_tagger_titles = {
    'mjj': ' - $M_{jj}$'
  , 'Deta': ' - $\Delta \eta$'
  , 'centrality': ' - Centrality'
  , 'Fcentrality': ' - Forward Centrality'
  , 'mjjj': ' - $M_{jjj}$'
}


def make_title(event_key):
    num_title = str(event_key[0])
    category_title = _category_titles[ event_key[1] ]
    selector_title = _selector_titles[ event_key[2] ]
    deep_filter_title = _deep_filter_titles[ event_key[3] ]
    tagger_title = _tagger_titles[ event_key[4] ]

    title = num_title+category_title
    title += selector_title+deep_filter_title+tagger_title

    return title
