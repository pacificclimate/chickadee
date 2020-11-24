import os
from pywps import Process, ComplexOutput, LiteralInput, FORMATS
from pywps.app.Common import Metadata
from netCDF4 import Dataset
from rpy2 import robjects

from wps_tools.utils import log_handler, collect_args, common_status_percentages
from wps_tools.io import log_level
from chickadee.utils import (
    logger,
    get_package,
    set_general_options,
    set_ca_options,
)
from chickadee.io import (
    gcm_file,
    obs_file,
    varname,
    num_cores,
    general_options_input,
    ca_options_input,
)


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
            **{"get_ClimDown": 5, "parallelization": 15, "write_files": 80},
        )

        inputs = (
            [
                gcm_file,
                obs_file,
                varname,
                num_cores,
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
            + general_options_input
            + ca_options_input
        )

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
        args = [arg[0] for arg in collect_args(request, self.workdir).values()]
        (
            gcm_file,
            obs_file,
            varname,
            num_cores,
            indices,
            weights,
            loglevel,
        ) = args[:7]

        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        log_handler(
            self,
            response,
            "Importing R package 'ClimDown'",
            logger,
            log_level=loglevel,
            process_step="get_ClimDown",
        )
        climdown = get_package("ClimDown")

        log_handler(
            self,
            response,
            "Setting R options",
            logger,
            log_level=loglevel,
            process_step="set_R_options",
        )
        # Uses general_options_input
        set_general_options(*args[7:13])
        # Uses ca_options_input
        set_ca_options(*args[13:])

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

        log_handler(
            self,
            response,
            "Calculating weights",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        # Run Constructed Analogue Step (CA)
        log_handler(
            self,
            response,
            "Calculating weights",
            logger,
            log_level=loglevel,
            process_step="process",
        )
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
