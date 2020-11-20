from pywps import LiteralInput, ComplexInput, FORMATS
from datetime import date

import logging


gcm_file = ComplexInput(
    "gcm_file",
    "GCM NetCDF file",
    abstract="Filename of GCM simulations",
    min_occurs=1,
    max_occurs=1,
    supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
)

obs_file = ComplexInput(
    "obs_file",
    "Observations NetCDF file",
    abstract="Filename of high-res gridded historical observations",
    min_occurs=1,
    max_occurs=1,
    supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
)

varname = LiteralInput(
    "varname",
    "Variable to Downscale",
    abstract="Name of the NetCDF variable to downscale (e.g. 'tasmax')",
    min_occurs=1,
    max_occurs=1,
    data_type="string",
)

out_file = LiteralInput(
    "out_file",
    "Output NetCDF File",
    abstract="Filename to create with the climate imprint outputs",
    min_occurs=0,
    max_occurs=1,
    data_type="string",
)

num_cores = LiteralInput(
    "num_cores",
    "Number of Cores",
    abstract="The number of cores to use for parallel execution",
    default=4,
    allowed_values=[1, 2, 3, 4],
    data_type="positiveInteger",
)

def options_input():
    inputs = [
        LiteralInput(
            "num_analogues",
            "Number of Analogues",
            abstract="The number of temporal analogues that the CA algorithm will search for andmatch.  The higher this number, the longer the execution time of the reorderingstep.",
            default=30,
            data_type="positiveInteger"
        ),
        LiteralInput(
            "start_date",
            "Start Date",
            abstract="Defines the stat of the calibration period",
            default=date(1971, 1, 1),
            data_type="date",
        ),
        LiteralInput(
            "end_date",
            "End Date",
            abstract="Defines the end of the calibration period",
            default=date(2005, 12, 31),
            data_type="date",
        ),
        LiteralInput(
            "units_bool",
            "Units Boolean",
            abstract="Whether to check the input units and convertthem to the target output units",
            default=True,
            data_type="boolean",
        ),
        LiteralInput(
            "n_pr_bool",
            "Negative Precipitation Boolean",
            abstract="Whether to check for and eliminate negativeprecipitation values",
            default=True,
            data_type="boolean",
        ),
        LiteralInput(
            "tasmax_units",
            "Tasmax Units",
            abstract="Units used for tasmax in output file",
            default="celsius",
            data_type="string"
        ),
        LiteralInput(
            "tasmin_units",
            "Tasmin Units",
            abstract="Units used for tasmin in output file",
            default="celsius",
            data_type="string"
        ),
        LiteralInput(
            "pr_units",
            "Precipitation Units",
            abstract="Units used for pr in output file",
            default="kg m-2 d-1",
            data_type="string"
        ),
    ]