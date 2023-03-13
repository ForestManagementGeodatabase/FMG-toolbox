def treecount(x):
    trees = []
    for val in x:
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
