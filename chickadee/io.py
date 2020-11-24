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


general_options_input = [
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
        data_type="string",
    ),
    LiteralInput(
        "tasmin_units",
        "Tasmin Units",
        abstract="Units used for tasmin in output file",
        default="celsius",
        data_type="string",
    ),
    LiteralInput(
        "pr_units",
        "Precipitation Units",
        abstract="Units used for pr in output file",
        default="kg m-2 d-1",
        data_type="string",
    ),
    LiteralInput(
        "max_gb",
        "Max BG",
        abstract="Anapproximate measure of how much RAM to use in the chunk I/O loop. It’s best to set this to about 1/3 to 1/4 of what you want the high-water mark to be",
        default=1.0,
        data_type="float",
    ),
]


ca_options_input = [
    LiteralInput(
        "num_analogues",
        "Number of Analogues",
        abstract="The number of temporal analogues that the CA algorithm will search for andmatch.  The higher this number, the longer the execution time of the reorderingstep.",
        default=30,
        data_type="positiveInteger",
    ),
    LiteralInput(
        "delta_days",
        "Delta Days",
        abstract="An integer describing the size of the window on either side of a day",
        default=45,
        data_type="positiveInteger",
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
        "trimmed_mean",
        "Trimmed Mean",
        abstract="The fraction (0 to 0.5) of observations to be trimmed from each end of the set of values before the mean is computed",
        default=0.0,
        data_type="float",
    ),
    LiteralInput(
        "tol",
        "Tol",
        default=0.1,
        data_type="float",
    ),
    LiteralInput(
        "expon",
        "Exponent",
        default=0.5,
        data_type="float",
    ),
]


qdm_options_input = [
    LiteralInput(
        "multiyear",
        "Multiyear",
        abstract="Apply over multi-year chunks",
        default=True,
        data_type="boolean",
    ),
    LiteralInput(
        "expand_multiyear",
        "Expand Multiyear",
        abstract="Fold incomplete multi-year block into previous",
        default=True,
        data_type="boolean",
    ),
    LiteralInput(
        "multiyear_window_length",
        "Multiyear Window Length",
        abstract="Number of years to run if multiyear is true",
        default=30,
        data_type="positiveInteger",
    ),
    LiteralInput(
        "trace",
        "Trace",
        abstract="Treat values below trace as left censored",
        default=0.005,
        data_type="float",
    ),
    LiteralInput(
        "jitter_factor",
        "Jitter Factor",
        abstract="Adds random noise to data to accomodate ties",
        default=0.01,
        data_type="float",
    ),
    LiteralInput(
        "pr_tau",
        "Pr Tau",
        abstract="Number of empirical quantiles for pr variable (NULL=sample length)",
        default=1001,
        data_type="positiveInteger",
    ),
    LiteralInput(
        "tasmax_tau",
        "Tasmax Tau",
        abstract="Number of empirical quantiles for tasmax variable (NULL=sample length)",
        default=101,
        data_type="positiveInteger",
    ),
    LiteralInput(
        "tasmin_tau",
        "Tasmin Tau",
        abstract="Number of empirical quantiles for tasmin variable (NULL=sample length)",
        default=101,
        data_type="positiveInteger",
    ),
    LiteralInput(
        "pr_seasonal",
        "Pr Seasonal",
        abstract="Apply over sliding 3-month windows",
        default=True,
        data_type="boolean",
    ),
    LiteralInput(
        "tasmax_seasonal",
        "Tasmax Seasonal",
        abstract="Apply over sliding 3-month windows",
        default=False,
        data_type="boolean",
    ),
    LiteralInput(
        "tasmin_seasonal",
        "Tasmin Seasonal",
        abstract="Apply over sliding 3-month windows",
        default=False,
        data_type="boolean",
    ),
    LiteralInput(
        "pr_ratio",
        "Pr Ratio",
        abstract="Preserve relative trends in a ratio variable",
        default=True,
        data_type="boolean",
    ),
    LiteralInput(
        "tasmax_ratio",
        "Tasmax Ratio",
        abstract="Preserve relative trends in a ratio variable",
        default=False,
        data_type="boolean",
    ),
    LiteralInput(
        "tasmin_ratio",
        "Tasmin Ratio",
        abstract="Preserve relative trends in a ratio variable",
        default=False,
        data_type="boolean",
    ),
]
