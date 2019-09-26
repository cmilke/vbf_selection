#select two highest pt jets
def highest_pt(event):
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
