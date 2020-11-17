from pywps import Process, LiteralInput
from pywps.app.Common import Metadata
from datetime import date
from wps_tools.utils import log_handler
from wps_tools.io import log_level, nc_output
from chickadee.utils import logger, get_package, collect_common_args, set_r_options
from chickadee.io import gcm_file, obs_file, varname, out_file, num_cores, end_date


class QDM(Process):
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

        super(QDM, self).__init__(
            self._handler,
            identifier="qdm",
            title="QDM",
            abstract="High-level wrapper for Quantile Delta Mapping (QDM)",
            metadata=[
                Metadata("NetCDF processing"),
                Metadata("Climate Data Operations"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    def _handler(self, request, response):
        (
            gcm_file,
            obs_file,
            varname,
            output_file,
            num_cores,
            end_date,
            loglevel,
        ) = collect_common_args(request)

        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        climdown = get_package("ClimDown")

        log_handler(
            self,
            response,
            "Processing QDM",
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

        climdown.qdm_netcdf_wrapper(obs_file, gcm_file, output_file, varname)

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

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )

        return response
