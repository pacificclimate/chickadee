from pywps import Process
from pywps.app.Common import Metadata
from rpy2 import robjects
from rpy2.rinterface_lib.embedded import RRuntimeError
from tempfile import TemporaryDirectory

# PCIC libraries
from wps_tools import logging, R, io, error_handling
import chickadee.utils as util
import chickadee.io as chick_io


class CI(Process):
    def __init__(self):
        self.status_percentage_steps = dict(
            logging.common_status_percentages,
            **{"get_ClimDown": 5, "set_R_options": 10, "parallelization": 15},
        )
        self.handler_inputs = [
            chick_io.gcm_file,
            chick_io.obs_file,
            chick_io.out_file,
            chick_io.num_cores,
            io.log_level,
        ]
        inputs = (
            self.handler_inputs
            + chick_io.general_options_input
            + chick_io.ci_options_input
        )

        outputs = [io.nc_output]

        super(CI, self).__init__(
            self._handler,
            identifier="ci",
            title="CI",
            abstract="Climate Imprint (CI) downscaling",
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
        util.raise_if_failed(response)
        logging.log_handler(
            self,
            response,
            "Importing R package 'ClimDown'",
            util.logger,
            log_level=loglevel,
            process_step="get_ClimDown",
        )
        climdown = R.get_package("ClimDown")
        util.raise_if_failed(response)
        logging.log_handler(
            self,
            response,
            "Setting R options",
            util.logger,
            log_level=loglevel,
            process_step="set_R_options",
        )
        # Uses general_options_input
        util.set_general_options(
            *util.select_args_from_input_list(args, chick_io.general_options_input)
        )

        # Uses ci_options_input
        util.set_ci_options(
            *util.select_args_from_input_list(args, chick_io.ci_options_input)
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
        util.raise_if_failed(response)
        doPar = R.get_package("doParallel")
        doPar.registerDoParallel(cores=num_cores)

        logging.log_handler(
            self,
            response,
            "Processing CI downscaling",
            util.logger,
            log_level=loglevel,
            process_step="process",
        )
        util.raise_if_failed(response)
        set_r_monitor, remove_r_monitor = util.create_r_progress_monitor(
            self, response, util.logger, loglevel
        )

        with TemporaryDirectory() as td:
            try:
                output_path = td + "/" + output_file
                set_r_monitor()
                climdown.ci_netcdf_wrapper(gcm_file, obs_file, output_path)
                remove_r_monitor()
            except RRuntimeError as e:
                remove_r_monitor()
                error_handling.custom_process_error(e)

            # stop parallelization
            doPar.stopImplicitCluster()
            util.raise_if_failed(response)
            logging.log_handler(
                self,
                response,
                "Building final output",
                util.logger,
                log_level=loglevel,
                process_step="build_output",
            )

            response.outputs["output"].file = output_path

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
