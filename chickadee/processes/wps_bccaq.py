import os
import re
from datetime import date
from pywps import Process, ComplexOutput, ComplexInput, LiteralInput, FORMATS
from pywps.app.Common import Metadata
from netCDF4 import Dataset

from wps_tools.utils import log_handler
from wps_tools.io import log_level
from chickadee.utils import logger, set_r_options, get_package


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
            ComplexInput(
                "gcm_file",
                "GCM NetCDF file",
                abstract="Filename of GCM simulations",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            ComplexInput(
                "obs_file",
                "Observations NetCDF file",
                abstract="Filename of high-res gridded historical observations",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            LiteralInput(
                "var",
                "Variable to Downscale",
                abstract="Name of the NetCDF variable to downscale",
                allowed_values=["tasmax", "tasmin", "pr"],
                data_type="string",
            ),
            LiteralInput(
                "end_date",
                "End Date",
                abstract="Defines the end of the calibration period",
                default=date(2005, 12, 31),
                data_type="date",
            ),
            LiteralInput(
                "out_file",
                "Output File Name",
                abstract="Path to output file",
                data_type="string",
            ),
            LiteralInput(
                "num_cores",
                "Number of Cores",
                abstract="The number of cores to use for parallel execution",
                default=4,
                allowed_values=[1, 2, 3, 4],
                data_type="positiveInteger",
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

    def collect_args(self, request):
        gcm_file = request.inputs["gcm_file"][0].file
        obs_file = request.inputs["obs_file"][0].file
        num_cores = request.inputs["num_cores"][0].data
        out_file = request.inputs["out_file"][0].data
        var = request.inputs["var"][0].data
        end_date = str(request.inputs["end_date"][0].data)

        return gcm_file, obs_file, num_cores, var, end_date, out_file

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

        gcm_file, obs_file, num_cores, var, end_date, out_file = self.collect_args(
            request
        )
        os.path.join(self.workdir, out_file)

        log_handler(
            self,
            response,
            "Downscaling GCM",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        # Set parallelization
        doPar = get_package("doParallel")
        doPar.registerDoParallel(cores=num_cores)

        # Set R options
        set_end = set_r_options()
        set_end(end_date)

        # Run ClimDown
        climdown = get_package("ClimDown")
        climdown.bccaq_netcdf_wrapper(gcm_file, obs_file, out_file, var)

        # Stop parallelization
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
