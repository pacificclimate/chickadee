from pywps import Process, LiteralInput
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError
from rpy2.rinterface_lib.embedded import RRuntimeError
from rpy2 import robjects

# PCIC libraries
import wps_tools as wpst
import chickadee.utils as util
import chickadee.io as chick_io


class CA(Process):
    """Constructed Analogue (CA) downscaling algorithm:
    Starts by spatially aggregating high-resolution gridded observations
    up to the scale of a GCM. Then it proceeds to bias correcting the GCM
    based on those observations. Finally, it conducts the search for temporal
    analogues. This involves taking each timestep in the GCM and searching for
    the top 30 closest timesteps in the gridded observations. For each of the
    30 closest "analogue" timesteps, CA records the integer number of the
    timestep (indices) and a weight for each of the analogues."""

    def __init__(self):
        self.status_percentage_steps = dict(
            wpst.logging.common_status_percentages,
            **{
                "get_ClimDown": 5,
                "set_R_options": 10,
                "parallelization": 15,
                "write_files": 80,
            },
        )

        self.handler_inputs = [
            chick_io.gcm_file,
            chick_io.obs_file,
            chick_io.varname,
            chick_io.num_cores,
            chick_io.out_file,
            wpst.io.vector_name,
            wpst.io.log_level,
        ]

        inputs = (
            self.handler_inputs
            + chick_io.general_options_input
            + chick_io.ca_options_input
        )

        outputs = [wpst.io.rda_output]

        super(CA, self).__init__(
            self._handler,
            identifier="ca",
            title="CA",
            abstract="Constructed Analogue (CA) downscaling algorithm",
            keywords=["constructed", "analogue", "downscaling"],
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
        args = wpst.io.collect_args(request, self.workdir)
        (
            gcm_file,
            obs_file,
            varname,
            num_cores,
            output_file,
            vector_name,
            loglevel,
        ) = util.select_args_from_input_list(args, self.handler_inputs)

        wpst.logging.log_handler(
            self,
            response,
            "Starting Process",
            util.logger,
            log_level=loglevel,
            process_step="start",
        )

        wpst.logging.log_handler(
            self,
            response,
            "Importing R package 'ClimDown'",
            util.logger,
            log_level=loglevel,
            process_step="get_ClimDown",
        )
        climdown = wpst.R.get_package("ClimDown")

        wpst.logging.log_handler(
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
        util.set_ca_options(
            *util.select_args_from_input_list(args, chick_io.ca_options_input)
        )

        wpst.logging.log_handler(
            self,
            response,
            "Setting parallelization",
            util.logger,
            log_level=loglevel,
            process_step="parallelization",
        )
        doPar = wpst.R.get_package("doParallel")
        doPar.registerDoParallel(cores=num_cores)

        wpst.logging.log_handler(
            self,
            response,
            "Calculating weights",
            util.logger,
            log_level=loglevel,
            process_step="process",
        )

        # Run Constructed Analogue Step (CA)
        wpst.logging.log_handler(
            self,
            response,
            "Calculating weights",
            util.logger,
            log_level=loglevel,
            process_step="process",
        )

        try:
            analogues = climdown.ca_netcdf_wrapper(gcm_file, obs_file, varname)
        except RRuntimeError as e:
            wpst.error_handling.custom_process_error(e)

        # Stop parallelization
        doPar.stopImplicitCluster()

        wpst.logging.log_handler(
            self,
            response,
            "Writing indices and weights lists to files",
            util.logger,
            log_level=loglevel,
            process_step="write_files",
        )
        wpst.R.r_valid_name(vector_name)
        wpst.R.save_python_to_rdata(vector_name, analogues, output_file)

        wpst.logging.log_handler(
            self,
            response,
            "Building final output",
            util.logger,
            log_level=loglevel,
            process_step="build_output",
        )

        response.outputs["rda_output"].file = output_file

        # Clear R global env
        robjects.r("rm(list=ls())")

        wpst.logging.log_handler(
            self,
            response,
            "Process Complete",
            util.logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
