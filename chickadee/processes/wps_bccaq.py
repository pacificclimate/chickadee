from pywps import Process, ComplexOutput, LiteralInput, FORMATS
from pywps.app.Common import Metadata
from netCDF4 import Dataset
from rpy2.robjects.packages import isinstalled, importr

from wps_tools.utils import log_handler
from wps_tools.io import log_level
from chickadee.utils import logger, set_r_options

# Install and import R packages
if not isinstalled("ClimDown"):
    utils = importr("utils")
    utils.install_packages("ClimDown")
if not isinstalled("doParallel"):
    utils = importr("utils")
    utils.install_packages("doParallel")

climdown = importr("ClimDown")
doPar = importr("doParallel")


class BCCAQ(Process):
    """Bias Correction/Constructed Analogues with Quantile mapping reordering:
    Full statistical downscaling of coarse scale global climate model (GCM)
    output to a fine spatial resolution"""

    def __init__(self):
        self.status_percentage_steps = {
            "start": 0,
            "process": 10,
            "build_output": 95,
            "complete": 100,
        }

        inputs = [
            LiteralInput(
                "gcm_file",
                "GCM NetCDF file",
                abstract="GCM simulations in NetCDF format",
                data_type="string",
            ),
            LiteralInput(
                "obs_file",
                "Observations NetCDF file",
                abstract="high-res gridded historical observations",
                data_type="string",
            ),
            LiteralInput(
                "var",
                "Variable to Downscale",
                abstract="Name of the NetCDF variable to downscale",
                data_type="string",
            ),
            LiteralInput(
                "end_date",
                "End Date",
                abstract="Defines the end of the calibration period",
                default="2005-12-31",
                data_type="string",
            ),
            LiteralInput(
                "out_file",
                "Output File Name",
                abstract="Path to output file",
                data_type="string",
            ),
            log_level,
        ]

        outputs = [
            ComplexOutput(
                "output",
                "Output",
                abstract="output netCDF file",
                supported_formats=[FORMATS.NETCDF],
            ),
        ]

        super(BCCAQ, self).__init__(
            self._handler,
            identifier="bccaq",
            title="BCCAQ",
            abstract="Full statistical downscaling of coarse scale global climate model (GCM) output to a fine spatial resolution",
            keywords=["downscaling"],
            metadata=[
                Metadata("PyWPS", "https://pywps.org/"),
                Metadata("Birdhouse", "http://bird-house.github.io/"),
                Metadata("PyWPS Demo", "https://pywps-demo.readthedocs.io/en/latest/"),
            ],
            version="0.1.0",
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

        gcm_file = request.inputs["gcm_file"][0].data
        obs_file = request.inputs["obs_file"][0].data
        var = request.inputs["var"][0].data
        end_date = request.inputs["end_date"][0].data
        out_file = request.inputs["out_file"][0].data

        log_handler(
            self,
            response,
            "Downscaling GCM",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        # Set R options
        set_end = set_r_options()
        set_end(end_date)

        # Set parallelization
        doPar.registerDoParallel(cores=4)

        # Run ClimDown
        climdown.bccaq_netcdf_wrapper(gcm_file, obs_file, out_file, var)

        # stop parallelization
        doPar.stopImplicitCluster()

        log_handler(
            self,
            response,
            "Building final output",
            logger,
            log_level=loglevel,
            process_step="build_output",
        )

        response.outputs["output"].file = out_file

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
