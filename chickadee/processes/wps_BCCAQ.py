import os
import re
from pywps import Process
from pywps.app.Common import Metadata
from netCDF4 import Dataset

from wps_tools.utils import log_handler
from wps_tools.io import log_level, nc_output
from chickadee.utils import (
    logger,
    set_end_date,
    get_package,
    collect_args,
    common_status_percentage,
    set_general_options,
    set_ca_options,
    set_qdm_options,
)
from chickadee.io import (
    gcm_file,
    obs_file,
    varname,
    out_file,
    num_cores,
    general_options_input,
    ca_options_input,
    qdm_options_input,
)


class BCCAQ(Process):
    """Bias Correction/Constructed Analogues with Quantile mapping reordering:
    Full statistical downscaling of coarse scale global climate model (GCM)
    output to a fine spatial resolution"""

    def __init__(self):
        self.status_percentage_steps = dict(
            common_status_percentage,
            **{"get_ClimDown": 5, "parallelization": 15},
        )

        inputs = [
            gcm_file,
            obs_file,
            varname,
            out_file,
            num_cores,
            log_level,
        ] + general_options_input + ca_options_input + qdm_options_input

        outputs = [nc_output]

        super(BCCAQ, self).__init__(
            self._handler,
            identifier="bccaq",
            title="BCCAQ",
            abstract="Full statistical downscaling of coarse scale global climate model (GCM) output to a fine spatial resolution",
            keywords=["downscaling"],
            metadata=[
                Metadata("NetCDF processing"),
                Metadata("Climate Data Operations"),
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
        args = collect_args(request)
        (
            gcm_file,
            obs_file,
            varname,
            out_file,
            num_cores,
            loglevel
        ) = args[:6]

        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        log_handler(
            self,
            response,
            "Importing R package 'ClimDown'",
            logger,
            log_level=loglevel,
            process_step="get_ClimDown",
        )
        climdown = get_package("ClimDown")

        log_handler(
            self,
            response,
            "Setting R options",
            logger,
            log_level=loglevel,
            process_step="set_R_options",
        )
        # Uses general_options_input
        set_general_options(*args[6:12])
        # Uses ca_options_input
        set_ca_options(*args[12:19])
        # Uses qdm_options_input
        set_qdm_options(*args[19:])

        log_handler(
            self,
            response,
            "Setting parallelization",
            logger,
            log_level=loglevel,
            process_step="parallelization",
        )
        doPar = get_package("doParallel")
        doPar.registerDoParallel(cores=num_cores)

        log_handler(
            self,
            response,
            "Downscaling GCM",
            logger,
            log_level=loglevel,
            process_step="process",
        )

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
