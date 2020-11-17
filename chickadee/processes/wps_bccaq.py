import os
import re
from pywps import Process, ComplexOutput, ComplexInput, LiteralInput, FORMATS
from pywps.app.Common import Metadata
from netCDF4 import Dataset

from wps_tools.utils import log_handler
from wps_tools.io import log_level, nc_output
from chickadee.utils import logger, set_r_options, get_package, collect_common_args
from chickadee.io import gcm_file, obs_file, varname, out_file, num_cores, end_date


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
            gcm_file,
            obs_file,
            varname,
            out_file,
            num_cores,
            end_date,
            log_level,
        ]

        outputs = [nc_output]

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
        end_date = str(request.inputs["end_date"][0].data)
        return end_date

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

        (
            gcm_file,
            obs_file,
            varname,
            out_file,
            num_cores,
            loglevel,
        ) = collect_common_args(request)
        end_date = self.collect_args(request)
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
        climdown.bccaq_netcdf_wrapper(gcm_file, obs_file, out_file, varname)

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
