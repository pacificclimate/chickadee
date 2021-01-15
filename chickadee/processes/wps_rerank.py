from rpy2 import robjects
from pywps import Process, ComplexInput, LiteralInput, FORMATS, Format
from pywps.app.Common import Metadata

from wps_tools.logging import log_handler, common_status_percentages
from wps_tools.R import get_package, load_rdata_to_python
from wps_tools.io import log_level, nc_output, collect_args
from chickadee.utils import (
    logger,
    set_general_options,
    select_args_from_input_list,
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

        self.handler_inputs = [
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
            ComplexInput(
                "analogues_object",
                "Analogues R object",
                abstract="R object containing the analogues produced from the CA step (suffix .rda)",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[
                    Format("application/x-gzip", extension=".rda", encoding="base64")
                ],
            ),
            LiteralInput(
                "analogues_name",
                "Name of analogues R object",
                abstract="Name of the R object containing the analogues",
                default="analogues",
                min_occurs=0,
                max_occurs=1,
                data_type="string",
            ),
        ]
        inputs = self.handler_inputs + general_options_input

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

    def load_rda(self, file_, obj_name):
        try:
            return load_rdata_to_python(file_, obj_name)
        except RRuntimeError:
            raise ProcessError(
                msg="Either your file is not a valid Rdata file or there is no object of that name is not found in this rda file"
            )

    def _handler(self, request, response):
        args = collect_args(request, self.workdir)
        (
            obs_file,
            varname,
            out_file,
            num_cores,
            loglevel,
            qdm_file,
            analogues_object,
            analogues_name,
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

        analogues = self.load_rda(analogues_object, analogues_name)

        try:
            climdown.rerank_netcdf_wrapper(qdm_file, obs_file, analogues, out_file, varname)
        except RRuntimeError as e:
            err = ProcessError(msg=e)
            if err.message == "Sorry, process failed. Please check server error log.":
                raise ProcessError(msg="Failure running rerank.netcdf.wrapper()")
            else:
                raise err

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
