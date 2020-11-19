import os
import re
from pywps import Process, LiteralInput
from pywps.app.Common import Metadata
from netCDF4 import Dataset

from wps_tools.utils import log_handler
from wps_tools.io import log_level, nc_output
from chickadee.utils import logger, set_end_date, get_package, collect_args
from chickadee.io import gcm_file, obs_file, varname, out_file, num_cores, end_date


class Rerank(Process):
    """Quantile Reranking fixes bias introduced by the Climate Analogues
    step by re-applying a simple quantile mapping bias correction at
    each grid box"""

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
            LiteralInput(
                "analogues_file",
                "Analogues R object",
                abstract="R object containing the analogues produced from the CA step (suffix .rds)",
                min_occurs=0,
                max_occurs=1,
                data_type="string",
            )
        ]

        outputs = [nc_output]

        super(Rerank, self).__init__(
            self._handler,
            identifier="rerank",
            title="Rerank",
            abstract="Quantile Reranking fixes bias introduced by the Climate Analogues step",
            keywords=["quantile reranking","rerank", "bias correction"],
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
            out_file,
            num_cores,
            loglevel,
            analogues
        ) = collect_args(request)

        log_handler(
            self,
            response,
            "Applying quantile mapping bias correction",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        # Set parallelization
        doPar = get_package("doParallel")
        doPar.registerDoParallel(cores=num_cores)

        # Get analogues R oject from file
        base = importr('base')
        analogues = base.readRDS(analogues_file)

        # Run rerank
        climdown = get_package("ClimDown")
        climdown.rerank_netcdf_wrapper(gcm_file, obs_file, analogues, out_file, varname)

        # Stop parallelization
        doPar.stopImplicitCluster()

        log_handler(
            self,
            response,
            "Building final output",
            logger,
            log_level=loglevel,
            process_step="build_output",
        )

        response.outputs["output"].file = out_file

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response