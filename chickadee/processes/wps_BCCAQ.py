from pywps import Process
from pywps.app.Common import Metadata
from rpy2.rinterface_lib.embedded import RRuntimeError
from rpy2 import robjects

from wps_tools.logging import log_handler, common_status_percentages
from wps_tools.io import collect_args, log_level, nc_output
from wps_tools.R import get_package
from wps_tools.error_handling import custom_process_error
from chickadee.utils import (
    logger,
    set_general_options,
    set_ca_options,
    set_qdm_options,
    select_args_from_input_list,
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
            common_status_percentages,
            **{"get_ClimDown": 5, "set_R_options": 10, "parallelization": 15},
        )

        self.handler_inputs = [
            gcm_file,
            obs_file,
            varname,
            out_file,
            num_cores,
            log_level,
        ]

        inputs = (
            self.handler_inputs
            + general_options_input
            + ca_options_input
            + qdm_options_input
        )

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
        args = collect_args(request, self.workdir)
        (
            gcm_file,
            obs_file,
            varname,
            out_file,
            num_cores,
            loglevel,
        ) = select_args_from_input_list(args, self.handler_inputs)
        print(gcm_file)
        print(obs_file)

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
        utils = get_package("utils")

        log_handler(
            self,
            response,
            "Setting R options",
            logger,
            log_level=loglevel,
            process_step="set_R_options",
        )
        set_general_options(*select_args_from_input_list(args, general_options_input))
        set_ca_options(*select_args_from_input_list(args, ca_options_input))
        set_qdm_options(*select_args_from_input_list(args, qdm_options_input))

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

        try:
            climdown.bccaq_netcdf_wrapper(gcm_file, obs_file, out_file, varname)
        except RRuntimeError as e:
            custom_process_error(e)

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

        # Clear R global env
        robjects.r("rm(list=ls())")

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
