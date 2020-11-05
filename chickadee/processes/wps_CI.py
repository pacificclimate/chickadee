from pywps import Process, ComplexInput, ComplexOutput, LiteralInput, FORMATS
from pywps.app.Common import Metadata
from rpy2.robjects.packages import isinstalled, importr

from wps_tools.utils import log_handler
from wps_tools.io import log_level
from chickadee.utils import logger

# Install and import R packages
if not isinstalled("ClimDown"):
    utils = importr("utils")
    utils.install_packages("ClimDown")
climdown = importr("ClimDown")


class CI(Process):
    def __init__(self):
        self.status_percentage_steps = {
            "start": 0,
            "process": 10,
            "build_output": 95,
            "complete": 100,
        }
        inputs = [
            log_level,
            LiteralInput(
                "gcm_file",
                "GCM NetCDF file",
                abstract="Filename of GCM simulations",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
            ),
            LiteralInput(
                "obs_file",
                "Observations NetCDF file",
                abstract="Filename of high-res gridded historical observations",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
            ),
            LiteralInput(
                "varname",
                "Variable to Downscale",
                abstract="Name of the NetCDF variable to downscale (e.g. 'tasmax')",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
            ),
            LiteralInput(
                "out_file",
                "Output NetCDF File",
                abstract="Filename to create with the climate imprint outputs",
                min_occurs=0,
                max_occurs=1,
                data_type="string",
            ),
            ComplexInput(
                "out_file",
                "Output NetCDF File",
                abstract="Filename to overwrite with the climate imprint outputs",
                min_occurs=0,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF],
            ),
        ]

        outputs = [
            ComplexOutput(
                "output",
                "Output",
                abstract="output netCDF file",
                supported_formats=[FORMATS.NETCDF],
            ),
        ]

        super(CI, self).__init__(
            self._handler,
            identifier="ci",
            title="CI",
            abstract="Climate Imprint (CI) downscaling",
            metadata=[
                Metadata("NetCDF processing"),
                Metadata("Climate Data Operations"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    def _handler(self, request, response):
        loglevel = request.inputs["loglevel"][0].data
        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )