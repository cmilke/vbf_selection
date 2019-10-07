# Do not allow any truth pileup in event
def no_pileup(event):
    for jet in event.jets:
        if jet.is_pileup: return False
    return True


# Allow only two truth non-pileup jets. 
def with_pileup(event):
    num_not_pu = 0
    for jet in event.jets:
        if not jet.is_pileup: num_not_pu += 1
    if num_not_pu > 2: return False
    else: return True


# Do not allow any jets marked by JVT or fJVT
def filter_by_JVT(event):
    for jet in event.jets:
        if jet.marked_pileup: return False
    return True


event_filters = {
    ''         : None
  , 'noPU'     : no_pileup
  , 'withPU'   : with_pileup
  , 'useJVT': filter_with_JVT
}


def filter_events(filter_key, event_list, auxiliary_list):
    filter_function = event_filters[filter_key]
    if filter_function == None: return auxiliary_list
    filtered_aux_list = []
    for event, aux_element in zip(event_list, auxiliary_list):
        if filter_function(event):
            filtered_aux_list.append(aux_element)
    return filtered_aux_list
