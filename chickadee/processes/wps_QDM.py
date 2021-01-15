from pywps import Process
from pywps.app.Common import Metadata
from rpy2 import robjects

from wps_tools.logging import log_handler, common_status_percentages
from wps_tools.R import get_package
from wps_tools.io import log_level, nc_output, collect_args
from chickadee.utils import (
    logger,
    set_general_options,
    set_qdm_options,
    select_args_from_input_list,
    run_wps_climdown
)
from chickadee.io import (
    gcm_file,
    obs_file,
    varname,
    out_file,
    num_cores,
    general_options_input,
    qdm_options_input,
)


class QDM(Process):
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

        inputs = self.handler_inputs + general_options_input + qdm_options_input

        outputs = [nc_output]

        super(QDM, self).__init__(
            self._handler,
            identifier="qdm",
            title="QDM",
            abstract="High-level wrapper for Quantile Delta Mapping (QDM)",
            metadata=[
                Metadata("NetCDF processing"),
                Metadata("Climate Data Operations"),
                Metadata("PyWPS", "https://pywps.org/"),
                Metadata("Birdhouse", "http://bird-house.github.io/"),
                Metadata("PyWPS Demo", "https://pywps-demo.readthedocs.io/en/latest/"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    @run_wps_climdown
    def qdm_netcdf_wrapper(self, climdown, obs_file, gcm_file, output_file, varname):
        climdown.qdm_netcdf_wrapper(obs_file, gcm_file, output_file, varname)

    def _handler(self, request, response):
        args = collect_args(request, self.workdir)
        (
            gcm_file,
            obs_file,
            varname,
            output_file,
            num_cores,
            loglevel,
        ) = select_args_from_input_list(args, self.handler_inputs)

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
        set_general_options(*select_args_from_input_list(args, general_options_input))
        set_qdm_options(*select_args_from_input_list(args, qdm_options_input))

        # Set parallelization
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
            "Processing QDM",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        self.qdm_netcdf_wrapper(climdown, obs_file, gcm_file, output_file, varname)
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
        response.outputs["output"].file = output_file

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
