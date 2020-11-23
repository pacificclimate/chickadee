from pywps import Process
from pywps.app.Common import Metadata
from wps_tools.utils import log_handler, collect_args, common_status_percentages
from wps_tools.io import log_level, nc_output
from chickadee.utils import (
    logger,
    get_package,
    set_end_date,
)
from chickadee.io import gcm_file, obs_file, varname, out_file, num_cores, end_date


class QDM(Process):
    def __init__(self):
        self.status_percentage_steps = dict(
            common_status_percentages,
            **{"get_ClimDown": 5, "parallelization": 10, "set_end_date": 15},
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
        (gcm_file, obs_file, varname, output_file, num_cores, end_date, loglevel,) = [
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

        # Get ClimDown
        log_handler(
            self,
            response,
            "Importing R package 'ClimDown'",
            logger,
            log_level=loglevel,
            process_step="get_ClimDown",
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

        # Set R option 'calibration.end'
        log_handler(
            self,
            response,
            "Setting R option 'calibration.end'",
            logger,
            log_level=loglevel,
            process_step="set_end_date",
        )
        set_end_date(end_date)

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
