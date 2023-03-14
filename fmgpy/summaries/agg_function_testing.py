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

def size_class_map(tr_dia):
    """Maps a size class categorical variable onto the tree diameter range
     as specified by USACE foresters

     Keyword Args
     tr_dia -- diameter of a given tree

     Details: written to function within the pandas .loc method
     """

    if 1 <= tr_dia <=6:
        return 'Sappling'
    if 6 < tr_dia <= 12:
        return 'Pole'
    if 12 < tr_dia <= 18:
        return 'Saw'
    if 18 < tr_dia <= 24:
        return 'Mature'
    if tr_dia > 24:
        return 'Over Mature'

def create_tree_table(prism_df):
    """Creates the tree dataframe for use in downstream forest summaries by checking:
        Column TR_DIA is set to 0 for no tree rows
        Column TR_SIZE is added and populated with size class based on tree diameter ranges
        Column TR_BA is added and populated with the eq (tree_count * BAF) / plot_count
        Column TR_DENS is added and populated with the eq (0.005454 * (tr_dia ** 2)) / plot_count

    Keyword Args
    prism_df -- the prism plot feature class directly imported as a dataframe

    Details: None
    """

    # Create Tree Data Frame
    tree_df = prism_df.drop(['CREATED_USER','CREATED_DATE', 'LAST_EDITED_USER','LAST_EDITED_DATE','SE_ANNO_CAD_DATA'],
                            axis=1,
                            errors='ignore')

    # Set TR_DIA to 0 if TR_SP is NoTree or None
    tree_df.loc[tree_df.TR_SP.isin(["NONE", "NoTree"]), 'TR_DIA'] = 0

    # Add a tree size class field (Sap, Pole, Saw, Mature, Over Mature)
    tree_df['TR_SIZE'] = tree_df['TR_DIA'].map(size_class_map)

    # Define constants for BA & Density calcs, assuming 1 tree, 1 plot
    tree_count = 1
    plot_count = 1
    baf = 10
    forester_constant = 0.005454

    # Add and Calculate BA column, then set BA to 0 where no tree
    tree_df['TR_BA'] = (tree_count * baf) / plot_count
    tree_df.loc[tree_df.TR_SP.isin(["NONE", "NoTree"]), 'TR_BA'] = 0

    # Add and calculate density column (TPA)
    tree_df['TR_DENS'] = (forester_constant * (tree_df['TR_DIA'] ** 2)) / plot_count

    return tree_df

def create_plot_table(tree_table)
    # Jam fixed & age details onto plot






