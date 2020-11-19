import os
from pywps import Process, ComplexOutput, LiteralInput, FORMATS
from pywps.app.Common import Metadata
from netCDF4 import Dataset
from rpy2 import robjects

from wps_tools.utils import log_handler
from wps_tools.io import log_level
from chickadee.utils import (
    logger,
    set_end_date,
    get_package,
    collect_args,
    common_status_percentage,
)
from chickadee.io import gcm_file, obs_file, varname, num_cores, end_date


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
            common_status_percentage,
            **{"write_files": 80},
        )

        inputs = [
            gcm_file,
            obs_file,
            varname,
            num_cores,
            end_date,
            LiteralInput(
                "indices",
                "Indices File",
                abstract="File name to store indices of analogue times steps (suffix .txt)",
                data_type="string",
            ),
            LiteralInput(
                "weights",
                "Weights File",
                abstract="File name to store weights of analogues (suffix .txt)",
                data_type="string",
            ),
            log_level,
        ]

        outputs = [
            ComplexOutput(
                "indices_file",
                "Indices File",
                abstract="File path with analogue indices",
                supported_formats=[FORMATS.TEXT],
            ),
            ComplexOutput(
                "weights_file",
                "Weights File",
                abstract="File path with analogue weights",
                supported_formats=[FORMATS.TEXT],
            ),
        ]

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

    def write_list_to_file(self, list_, filename):
        with open(filename, "w") as file_:
            for line in list_:
                for item in line:
                    file_.write(f"{item}\n")

    def _handler(self, request, response):
        loglevel = request.inputs["loglevel"][0].data
        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        (
            gcm_file,
            obs_file,
            varname,
            num_cores,
            end_date,
            indices,
            weights,
            log_level,
        ) = collect_args(request)

        log_handler(
            self,
            response,
            "Calculating weights",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        # Set parallelization
        doPar = get_package("doParallel")
        doPar.registerDoParallel(cores=num_cores)

        # Set R options
        set_end_date(end_date)

        # Run Constructed Analogue Step (CA)
        climdown = get_package("ClimDown")
        analogues = climdown.ca_netcdf_wrapper(gcm_file, obs_file, varname)

        # Stop parallelization
        doPar.stopImplicitCluster()

        log_handler(
            self,
            response,
            "Writing indices and weights lists to files",
            logger,
            log_level=loglevel,
            process_step="write_files",
        )

        self.write_list_to_file(analogues[0], indices)
        self.write_list_to_file(analogues[1], weights)

        log_handler(
            self,
            response,
            "Building final output",
            logger,
            log_level=loglevel,
            process_step="build_output",
        )

        response.outputs["indices_file"].file = indices
        response.outputs["weights_file"].file = weights

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
