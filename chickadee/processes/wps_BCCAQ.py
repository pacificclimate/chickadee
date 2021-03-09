from pywps import Process
from pywps.app.Common import Metadata
from rpy2.rinterface_lib.embedded import RRuntimeError
from rpy2 import robjects

import wps_tools as wpst
import chickadee.utils as util
import chickadee.io as chick_io


class BCCAQ(Process):
    """Bias Correction/Constructed Analogues with Quantile mapping reordering:
    Full statistical downscaling of coarse scale global climate model (GCM)
    output to a fine spatial resolution"""

    def __init__(self):
        self.status_percentage_steps = dict(
            wpst.logging.common_status_percentages,
            **{"get_ClimDown": 5, "set_R_options": 10, "parallelization": 15},
        )

        self.handler_inputs = [
            chick_io.gcm_file,
            chick_io.obs_file,
            chick_io.varname,
            chick_io.out_file,
            chick_io.num_cores,
            wpst.io.log_level,
        ]

        inputs = (
            self.handler_inputs
            + chick_io.general_options_input
            + chick_io.ca_options_input
            + chick_io.qdm_options_input
        )

        outputs = [wpst.io.nc_output]

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
        args = wpst.io.collect_args(request, self.workdir)
        (
            gcm_file,
            obs_file,
            varname,
            out_file,
            num_cores,
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
        util.set_qdm_options(
            *util.select_args_from_input_list(args, chick_io.qdm_options_input)
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
            "Downscaling GCM",
            util.logger,
            log_level=loglevel,
            process_step="process",
        )

        try:
            climdown.bccaq_netcdf_wrapper(gcm_file, obs_file, out_file, varname)
        except RRuntimeError as e:
            wpst.error_handling.custom_process_error(e)

        doPar.stopImplicitCluster()

        wpst.logging.log_handler(
            self,
            response,
            "Building final output",
            util.logger,
            log_level=loglevel,
            process_step="build_output",
        )

        response.outputs["output"].file = out_file

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
