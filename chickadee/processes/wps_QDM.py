from pywps import Process
from pywps.app.Common import Metadata
from rpy2 import robjects
from rpy2.rinterface_lib.embedded import RRuntimeError

# PCIC libraries
from wps_tools import logging, R, io, error_handling
import chickadee.utils as util
import chickadee.io as chick_io


class QDM(Process):
    def __init__(self):
        self.status_percentage_steps = dict(
            logging.common_status_percentages,
            **{"get_ClimDown": 5, "set_R_options": 10, "parallelization": 15},
        )
        self.handler_inputs = [
            chick_io.gcm_file,
            chick_io.obs_file,
            chick_io.varname,
            chick_io.out_file,
            chick_io.num_cores,
            io.log_level,
        ]

        inputs = (
            self.handler_inputs
            + chick_io.general_options_input
            + chick_io.qdm_options_input
        )

        outputs = [io.nc_output]

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

    def _handler(self, request, response):
        args = io.collect_args(request.inputs, self.workdir)
        (
            gcm_file,
            obs_file,
            varname,
            output_file,
            num_cores,
            loglevel,
        ) = util.select_args_from_input_list(args, self.handler_inputs)

        logging.log_handler(
            self,
            response,
            "Starting Process",
            util.logger,
            log_level=loglevel,
            process_step="start",
        )

        logging.log_handler(
            self,
            response,
            "Importing R package 'ClimDown'",
            util.logger,
            log_level=loglevel,
            process_step="get_ClimDown",
        )
        climdown = R.get_package("ClimDown")

        logging.log_handler(
            self,
            response,
            "Setting R options",
            util.logger,
            log_level=loglevel,
            process_step="set_R_options",
        )
        util.set_general_options(
            *util.select_args_from_input_list(args, chick_io.general_options_input)
        )
        util.set_qdm_options(
            *util.select_args_from_input_list(args, chick_io.qdm_options_input)
        )

        # Set parallelization
        logging.log_handler(
            self,
            response,
            "Setting parallelization",
            util.logger,
            log_level=loglevel,
            process_step="parallelization",
        )
        doPar = R.get_package("doParallel")
        doPar.registerDoParallel(cores=num_cores)

        logging.log_handler(
            self,
            response,
            "Processing QDM",
            util.logger,
            log_level=loglevel,
            process_step="process",
        )
        try:
            climdown.qdm_netcdf_wrapper(obs_file, gcm_file, output_file, varname)
        except RRuntimeError as e:
            error_handling.custom_process_error(e)

        # stop parallelization
        doPar.stopImplicitCluster()

        logging.log_handler(
            self,
            response,
            "Building final output",
            util.logger,
            log_level=loglevel,
            process_step="build_output",
        )
        response.outputs["output"].file = output_file

        # Clear R global env
        robjects.r("rm(list=ls())")

        logging.log_handler(
            self,
            response,
            "Process Complete",
            util.logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
