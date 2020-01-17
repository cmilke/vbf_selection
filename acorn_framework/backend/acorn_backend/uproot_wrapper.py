import uproot


def unnest_list(nested_list, container_template):
    expanded_list = []
    for item in nested_list:
        if isinstance(item, str): 
            expanded_list.append(item)
            container_template[item] = (1, None)
        else:
            key, nested_sublist = item
            nested_container = {}
            pre_expansion_size = len(expanded_list)
            expanded_list += unnest_list(nested_sublist, nested_container)
            size = len(expanded_list) - pre_expansion_size
            container_template[key] = (size, nested_container)
    return expanded_list



'''
WARNING: The values "returned" by the two below functions (e.g. values such as event['reco_jets'])
are GENERATORS, and therefore each element the generator produces (e.g. each reco jet)
can only be accessed ONCE. After you cycle through the values (e.g. via a for loop),
you CANNOT access the elements again.
If you have a situation where you need to access the same elements many times,
you should not access the generator directly.
Instead, you should first convert it to a list ( e.g.: 
    reco_jets = [ rj.copy() for rj in event['reco_jets'] ]
).
Converting to a list in this fashion will allow you to access the same elements
as many times as you want. (Converting to a list is slower and less memory efficient,
which is why lists are not produced by default)
'''



def nested_generator(container_template, container_size, superindex, entry):
    subgroup_container = { key: None for key in container_template }
    subrange = slice(superindex,superindex+container_size)
    for subentry in zip(*entry[subrange]):
        subindex = 0
        for key, (size, sub_template) in container_template.items():
            if sub_template == None:
                subgroup_container[key] = subentry[subindex]
            else:
                subgroup_container[key] = nested_generator(sub_template,size,subindex,subentry)
            subindex += size
        yield subgroup_container


def event_iterator(ntuple_list, tree_name, nested_branch_list, events_to_read):
    bucket_size = 10000

    container_template = {}
    branch_list = unnest_list(nested_branch_list, container_template)
    event_container = { key: None for key in container_template }

    events_read = 0
    for ntuple_file in ntuple_list:
        print('\nnutple file: ' + ntuple_file)
        tree = uproot.rootio.open(ntuple_file)[tree_name]
        tree_iterator = tree.iterate(branches=branch_list, entrysteps=bucket_size) 
        for basket_number, basket in enumerate(tree_iterator):
            print('Basket: ' + str(basket_number) )
            for entry in zip(*basket.values()):
                index = 0
                for key, (size, sub_template) in container_template.items():
                    if sub_template == None:
                        event_container[key] = entry[index] 
                    else:
                        event_container[key] = nested_generator(sub_template,size,index,entry)
                    index += size
                yield event_container
                events_read += 1
                if events_to_read != None and events_read >= events_to_read: return
