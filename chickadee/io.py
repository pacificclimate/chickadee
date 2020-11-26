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
        abstract="Check the input units and convert them to the target output units",
        max_occurs=1,
        default=True,
        data_type="boolean",
    ),
    LiteralInput(
        "n_pr_bool",
        "Negative Precipitation Boolean",
        abstract="Check for and eliminate negative precipitation values",
        max_occurs=1,
        default=True,
        data_type="boolean",
    ),
    LiteralInput(
        "tasmax_units",
        "Tasmax Units",
        abstract="Units used for tasmax in output file",
        max_occurs=1,
        default="celsius",
        data_type="string",
    ),
    LiteralInput(
        "tasmin_units",
        "Tasmin Units",
        abstract="Units used for tasmin in output file",
        max_occurs=1,
        default="celsius",
        data_type="string",
    ),
    LiteralInput(
        "pr_units",
        "Precipitation Units",
        abstract="Units used for pr in output file",
        max_occurs=1,
        default="kg m-2 d-1",
        data_type="string",
    ),
    LiteralInput(
        "max_gb",
        "Max GB",
        abstract="Anapproximately how much RAM to use in the chunk I/O loop. It’s best to set this to about 1/3 to 1/4 of what you want the high-water mark to be",
        max_occurs=1,
        default=1.0,
        data_type="float",
    ),
    LiteralInput(
        "start_date",
        "Start Date",
        abstract="Defines the stat of the calibration period",
        max_occurs=1,
        default=date(1971, 1, 1),
        data_type="date",
    ),
    LiteralInput(
        "end_date",
        "End Date",
        abstract="Defines the end of the calibration period",
        max_occurs=1,
        default=date(2005, 12, 31),
        data_type="date",
    ),
]


ca_options_input = [
    LiteralInput(
        "num_analogues",
        "Number of Analogues",
        abstract="The number of temporal analogues that the CA algorithm will search for and match. The higher this number, the longer the execution time of the reordering step.",
        max_occurs=1,
        default=30,
        data_type="positiveInteger",
    ),
    LiteralInput(
        "delta_days",
        "Delta Days",
        abstract="An integer describing the size of the window on either side of a day - Not recommeded to change",
        max_occurs=1,
        default=45,
        data_type="positiveInteger",
    ),
    LiteralInput(
        "trimmed_mean",
        "Trimmed Mean",
        abstract="The fraction (0 to 0.5) of observations to be trimmed from each extreme of the distribution before the mean is computed - Not recommended to change",
        max_occurs=1,
        default=0.0,
        data_type="float",
    ),
    LiteralInput(
        "tol",
        "Tuning Parameter",
        abstract="Tuning parameter used in ridge regression to calculate weights - Not recommended to change ",
        max_occurs=1,
        default=0.1,
        data_type="float",
    ),
]


qdm_options_input = [
    LiteralInput(
        "multiyear",
        "Multiyear",
        abstract="Apply over multi-year chunks - Not recommended to change",
        max_occurs=1,
        default=True,
        data_type="boolean",
    ),
    LiteralInput(
        "expand_multiyear",
        "Expand Multiyear",
        abstract="Fold incomplete multi-year block into previous - Not recommended to change",
        max_occurs=1,
        default=True,
        data_type="boolean",
    ),
    LiteralInput(
        "multiyear_window_length",
        "Multiyear Window Length",
        abstract="Number of years to run if multiyear is true - Not recommended to change",
        max_occurs=1,
        default=30,
        data_type="positiveInteger",
    ),
    LiteralInput(
        "trace",
        "Trace",
        abstract="Treat values below trace as left censored - Not recommended to change",
        max_occurs=1,
        default=0.005,
        data_type="float",
    ),
    LiteralInput(
        "jitter_factor",
        "Jitter Factor",
        abstract="Adds random noise to data to accomodate ties - Not recommended to change",
        max_occurs=1,
        default=0.01,
        data_type="float",
    ),
    LiteralInput(
        "pr_tau",
        "Pr Tau",
        abstract="Number of empirical quantiles for pr variable (NULL=sample length) - Not recommended to change",
        max_occurs=1,
        default=1001,
        data_type="positiveInteger",
    ),
    LiteralInput(
        "tasmax_tau",
        "Tasmax Tau",
        abstract="Number of empirical quantiles for tasmax variable (NULL=sample length) - Not recommended to change",
        max_occurs=1,
        default=101,
        data_type="positiveInteger",
    ),
    LiteralInput(
        "tasmin_tau",
        "Tasmin Tau",
        abstract="Number of empirical quantiles for tasmin variable (NULL=sample length) - Not recommended to change",
        max_occurs=1,
        default=101,
        data_type="positiveInteger",
    ),
    LiteralInput(
        "pr_seasonal",
        "Pr Seasonal",
        abstract="Apply over sliding 3-month windows - Not recommended to change",
        max_occurs=1,
        default=True,
        data_type="boolean",
    ),
    LiteralInput(
        "tasmax_seasonal",
        "Tasmax Seasonal",
        abstract="Apply over sliding 3-month windows - Not recommended to change",
        max_occurs=1,
        default=False,
        data_type="boolean",
    ),
    LiteralInput(
        "tasmin_seasonal",
        "Tasmin Seasonal",
        abstract="Apply over sliding 3-month windows - Not recommended to change",
        max_occurs=1,
        default=False,
        data_type="boolean",
    ),
    LiteralInput(
        "pr_ratio",
        "Pr Ratio",
        abstract="Preserve relative trends in pr ratio variable - Not recommended to change",
        max_occurs=1,
        default=True,
        data_type="boolean",
    ),
    LiteralInput(
        "tasmax_ratio",
        "Tasmax Ratio",
        abstract="Preserve relative trends in tasmax ratio variable - Not recommended to change",
        max_occurs=1,
        default=False,
        data_type="boolean",
    ),
    LiteralInput(
        "tasmin_ratio",
        "Tasmin Ratio",
        abstract="Preserve relative trends in tasmin ratio variable - Not recommended to change",
        max_occurs=1,
        default=False,
        data_type="boolean",
    ),
]
