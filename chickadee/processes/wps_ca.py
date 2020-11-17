import os
import re
from pywps import Process, ComplexOutput, ComplexInput, LiteralInput, FORMATS
from pywps.app.Common import Metadata
from netCDF4 import Dataset
from rpy2 import robjects

from wps_tools.utils import log_handler
from wps_tools.io import log_level
from chickadee.utils import logger, set_r_options, get_package
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
            num_cores,
            end_date,
            ComplexInput(
                "indices_file",
                "Indices File",
                abstract="File to store indices of analogue times steps",
                supported_formats=[FORMATS.TEXT],
            ),
            ComplexInput(
                "weight_file",
                "Weight File",
                abstract="File to store weights of analogues",
                supported_formats=[FORMATS.TEXT],
            ),
            log_level,
        ]

        outputs = [
            ComplexOutput(
                "indices",
                "Indices",
                abstract="File path with analogue indices",
                supported_formats=[FORMATS.TEXT],
            ),
            ComplexOutput(
                "weights",
                "Weights",
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

    def collect_args(self, request):
        gcm_file = request.inputs["gcm_file"][0].file
        obs_file = request.inputs["obs_file"][0].file
        num_cores = request.inputs["num_cores"][0].data
        var = request.inputs["var"][0].data
        end_date = str(request.inputs["end_date"][0].data)
        indices_file = request.inputs["indices_file"][0].data
        weights_file = request.inputs["weights_file"][0].data

        return gcm_file, obs_file, num_cores, var, end_date, indices_file, weights_file

    def write_list_to_file(self, list_, filename):
        with open(filename, "r") as file_:
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
            num_cores,
            var,
            end_date,
            indices_file,
            weights_file,
        ) = self.collect_args(request)

        log_handler(
            self,
            response,
            "Downscaling GCM",
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

        # Run Constructed Analogue Step (CA)
        climdown = get_package("ClimDown")
        analogues = climdown.ca_netcdf_wrapper(gcm_file, obs_file, var)

        # Stop parallelization
        doPar.stopImplicitCluster()

        # Write indices and weights to files
        self.write_list_to_file(analogues[0], indices_file.name)
        self.write_list_to_file(analogues[1], weights_file.name)

        log_handler(
            self,
            response,
            "Building final output",
            logger,
            log_level=loglevel,
            process_step="build_output",
        )

        response.outputs["indices"].file = indices_file.name
        response.outputs["weights"].file = weights_file.name

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
