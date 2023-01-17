"""Floodplain Forest Metrics Summary Table

Create a table of metrics used to calculate the Floodplain Forest HSI.

:param: output_gdb      str; Path the output geodatabase.
:param: level           str; The FMG hierarchical level. One of: "unit",
                        "site", "stand", "plot".
:param: age             str; Path to the FMG "Age" point feature class.
:param: fixed           str; Path to the FMG "Fixed" point feature class.
:param: prism           str; Path to the FMG "Prism" point feature class.

:return: A geodatabase table containing a field for each metric in the
Floodplain Forest HSI.

"""
import os
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import pandas as pd
import importlib
import forest_calcs

# Ensure changes are reloaded during interactive development session
importlib.reload(arcpy)
importlib.reload(forest_calcs)

arcpy.env.overwriteOutput = True


def main():
    # create dataframes
    age_df = pd.DataFrame.spatial.from_featureclass(age)
    fixed_df = pd.DataFrame.spatial.from_featureclass(fixed)
    prism_df = pd.DataFrame.spatial.from_featureclass(prism)

    # Determine summary level
    level_field = forest_calcs.fmg_level(level)

    # Canopy Cover, Percent
    canopy_cover = forest_calcs.cover_pct(fixed_df, level)
    arcpy.AddMessage("Calculated canopy cover")

    # Desired Forest Type, Percent

    # Invasive Species, Percent

    # Regeneration (Desired Stocking, Percent)

    # Horizontal Structural Diversity

    # Vertical Structural Diversity

    # Size Class Diversity

    # Standing Dead Wood

    # Species Diversity

    # Combine metrics
    metrics_df = canopy_cover
    arcpy.AddMessage("Combined metrics")

    # Write summary table
    metrics_path = os.path.join(output_gdb, "floodplain_forest_metrics")
    metrics_df.spatial.to_table(metrics_path,
                                overwrite=True,
                                sanitize_columns=False)
    arcpy.AddMessage("Saved table")


if __name__ == "__main__":
    # Get input parameters
    output_gdb = arcpy.GetParameterAsText(0)
    level = arcpy.GetParameterAsText(1)
    age = arcpy.GetParameterAsText(2)
    fixed = arcpy.GetParameterAsText(3)
    prism = arcpy.GetParameterAsText(4)

    main()

