from pywps import Process
from pywps.app.Common import Metadata
from datetime import date
from wps_tools.utils import log_handler
from wps_tools.io import log_level, nc_output
from chickadee.utils import (
    logger,
    get_package,
    collect_common_args,
    set_r_options,
    common_status_percentage,
)
from chickadee.io import gcm_file, obs_file, varname, out_file, num_cores, end_date


class QDM(Process):
    def __init__(self):
        self.status_percentage_steps = common_status_percentage.update(
            {"parallelization": 5, "set_end_date": 10, "process": 15}
        )
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

        # Set R options
        log_handler(
            self,
            response,
            "Setting R option 'calibration.end'",
            logger,
            log_level=loglevel,
            process_step="set_end_date",
        )

        set_end = set_r_options()
        set_end(end_date)

        log_handler(
            self,
            response,
            "Processing QDM",
            logger,
            log_level=loglevel,
            process_step="process",
        )

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