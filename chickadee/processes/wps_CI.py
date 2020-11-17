from pywps import Process
from pywps.app.Common import Metadata

from wps_tools.utils import log_handler
from wps_tools.io import log_level, nc_output
from chickadee.utils import logger, get_package, collect_common_args
from chickadee.io import gcm_file, obs_file, varname, out_file, num_cores


class CI(Process):
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
            log_level,
        ]

        outputs = [nc_output]

        super(CI, self).__init__(
            self._handler,
            identifier="ci",
            title="CI",
            abstract="Climate Imprint (CI) downscaling",
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
            "Processing CI downscaling",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        # Set parallelization
        doPar = get_package("doParallel")
        doPar.registerDoParallel(cores=num_cores)

        climdown.ci_netcdf_wrapper(gcm_file, obs_file, output_file, varname)

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
