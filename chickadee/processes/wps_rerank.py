import os
import re
from pywps import Process, LiteralInput, ComplexInput, FORMATS
from pywps.app.Common import Metadata
from netCDF4 import Dataset

from wps_tools.utils import log_handler, common_status_percentages, collect_args
from wps_tools.io import log_level, nc_output
from chickadee.utils import (
    logger,
    get_package,
    set_general_options,
)
from chickadee.io import (
    gcm_file,
    obs_file,
    varname,
    out_file,
    num_cores,
    general_options_input,
)


class Rerank(Process):
    """Quantile Reranking fixes bias introduced by the Climate Analogues
    step by re-applying a simple quantile mapping bias correction at
    each grid box"""

    def __init__(self):
        self.status_percentage_steps = dict(
            common_status_percentages,
            **{"get_ClimDown": 5, "set_R_options": 10, "parallelization": 15},
        )

        inputs = [
            obs_file,
            varname,
            out_file,
            num_cores,
            log_level,
            ComplexInput(
                "qdm_file",
                "QDM NetCDF file",
                abstract="Filename of output from QDM step",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            LiteralInput(
                "analogues_object",
                "Analogues R object",
                abstract="R object containing the analogues produced from the CA step (suffix .rds)",
                min_occurs=0,
                max_occurs=1,
                data_type="string",
            ),
        ] + general_options_input

        outputs = [nc_output]

        super(Rerank, self).__init__(
            self._handler,
            identifier="rerank",
            title="Rerank",
            abstract="Quantile Reranking fixes bias introduced by the Climate Analogues step",
            keywords=["quantile reranking", "rerank", "bias correction"],
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
        args = [arg[0] for arg in collect_args(request, self.workdir).values()]
        (
            obs_file,
            varname,
            out_file,
            num_cores,
            loglevel,
            qdm_file,
            analogues_object,
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
            "Applying quantile mapping bias correction",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        # Get analogues R oject from file
        base = get_package("base")
        with open(analogues_object):
            analogues = base.readRDS(analogues_object)

        climdown.rerank_netcdf_wrapper(qdm_file, obs_file, analogues, out_file, varname)

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
