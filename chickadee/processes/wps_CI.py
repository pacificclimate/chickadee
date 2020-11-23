from pywps import Process
from pywps.app.Common import Metadata

from wps_tools.utils import log_handler, collect_args, common_status_percentages
from wps_tools.io import log_level, nc_output
from chickadee.utils import logger, get_package
from chickadee.io import gcm_file, obs_file, varname, out_file, num_cores


class CI(Process):
    def __init__(self):
        self.status_percentage_steps = common_status_percentages
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
        logger.critical(str(collect_args(request, self.workdir).values()))
        (gcm_file, obs_file, varname, output_file, num_cores, loglevel,) = [
            arg[0] for arg in collect_args(request, self.workdir).values()
        ]

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
