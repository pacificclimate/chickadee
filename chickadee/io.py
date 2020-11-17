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

end_date = LiteralInput(
    "end_date",
    "End Date",
    abstract="Defines the end of the calibration period",
    default=date(2005, 12, 31),
    data_type="date",
)
