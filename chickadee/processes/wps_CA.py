import os
from pywps import Process, ComplexOutput, LiteralInput, Format
from pywps.app.Common import Metadata
from netCDF4 import Dataset
from rpy2 import robjects

from wps_tools.utils import log_handler, collect_args, common_status_percentages, get_package, save_python_to_rdata
from wps_tools.io import log_level, vector_name, rda_output
from chickadee.utils import (
    logger,
    set_general_options,
    set_ca_options,
    select_args_from_input_list,
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
            common_status_percentages,
            **{
                "get_ClimDown": 5,
                "set_R_options": 10,
                "parallelization": 15,
                "write_files": 80,
            },
        )

        self.handler_inputs = [
            gcm_file,
            obs_file,
            varname,
            num_cores,
            LiteralInput(
                "output_file",
                "Output file name",
                abstract="Filename to store the output Rdata (extension .rda)",
                min_occurs=0,
                max_occurs=1,
                default="output.rda",
                data_type="string",
            ),
            vector_name,
            log_level,
        ]

        inputs = self.handler_inputs + general_options_input + ca_options_input

        outputs = [rda_output]

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
        args = collect_args(request, self.workdir)
        (
            gcm_file,
            obs_file,
            varname,
            num_cores,
            output_file,
            vector_name,
            loglevel,
        ) = select_args_from_input_list(args, self.handler_inputs)

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
        set_general_options(*select_args_from_input_list(args, general_options_input))
        set_ca_options(*select_args_from_input_list(args, ca_options_input))

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
        save_python_to_rdata(vector_name, analogues, output_file)

        log_handler(
            self,
            response,
            "Building final output",
            logger,
            log_level=loglevel,
            process_step="build_output",
        )

        response.outputs["rda_output"].file = output_file

        # Clear R global env
        robjects.r("rm(list=ls())")

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
