def treecount(tr_sp):
    trees = []
    for val in tr_sp:
        if val == 'NoTree':
            continue
        elif val == 'NONE':
            continue
        elif val == '':
            continue
        elif val == ' ':
            continue
        elif val is None:
            continue
        else:
            trees.append(val)
    return float(len(trees))

def plotcount(x):
    return float(x.nunique())




