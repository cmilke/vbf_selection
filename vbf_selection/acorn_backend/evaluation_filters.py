def no_pileup(event):
    if event.is_background: return True
    for jet in event.jets:
        if jet.is_pileup: return False
    return True


def with_pileup(event):
    if event.is_background: return True
    for jet in event.jets:
        if not ( jet.is_pileup or jet.is_truth_quark() ): return False
    return True


event_filters = {
    ''      : None
  , 'noPU'  : no_pileup
  , 'withPU': with_pileup
}


def filter_events(filter_key, event_list, auxiliary_list):
    filter_function = event_filters[filter_key]
    if filter_function == None: return auxiliary_list
    filtered_aux_list = []
    for event, aux_element in zip(event_list, auxiliary_list):
        if filter_function(event):
            filtered_aux_list.append(aux_element)
    return filtered_aux_list
