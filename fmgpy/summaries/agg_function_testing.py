def treecount(tr_sp):
    """Counts trees, excluding no tree records.

    Keyword Arguments:
    tr_sp -- Input tree species column.

    Details: Function returns a single value and is to be used within a
    dataframe to create a tree count column (.groupby, .agg).
    """
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


def plotcount(PID):
    """Counts unique plots, including no tree plots.

    Keyword Arguments:
    PID -- Input plot ID column.

    Details: Function returns a single value and is to be used within a
    dataframe to create a plot count column (.groupby, .agg).
    """
    return float(x.nunique())


def create_tree_table(prism_df)
    # Set TR_DIA to 0 if TR_SP is NoTree or None
    # Add a tree size class field (Sap, Pole, Saw, Mature, Over Mature)
    # Add and Calculate BA column (will always be 10, unless NoTree but use equation)
    # Add and calculate density column (TPA)

def create_plot_table(tree_table)
    # Jam fixed & age details onto plot






