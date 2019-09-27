#Select two highest pt jets
def highest_pt_selector(event):
    jet_idents = [-1,-1]
    max_pts = [-1,-1]
    for index, jet in enumerate(event):
        if jet.pt > max_pts[0]:
            max_pts[1] = max_pts[0]
            jet_idents[1] = jet_idents[0]
            max_pts[0] = jet.pt
            jet_idents[0] = index
        elif jet.pt > max_pts[1]:
            max_pts[1] = jet.pt
            jet_idents[1] = index
    return jet_idents

def maximal_eta_selector(event):
    jet_idents = [-1,-1]
    max_delta_eta = -1
    num_jets = len(event)
    for i in range(0, num_jets):
        eta0 = event[i].eta
        for j in range(i+1, num_jets):
            eta1 = event[j].eta
            delta_eta = abs(eta0 - eta1)
            if delta_eta > max_delta_eta:
                max_delta_eta = delta_eta
                jet_idents = [i,j]
    return jet_idents



#Return the first two jets.
#Should really only be used for 2 jet events
def null_selector(event): return [0,1]


#Selects the correct vbf jets based on truth info
#Returns the first two if background
def truth_selector(event):
    jet_idents = []
    for index, jet in enumerate(event):
        if jet.is_truth_quark: jet_idents.append(index)

    if len(jet_idents) == 2: return jet_idents
    else: return [0,1]
