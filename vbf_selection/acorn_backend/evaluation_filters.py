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
