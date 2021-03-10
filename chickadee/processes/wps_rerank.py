from rpy2 import robjects
from rpy2.rinterface_lib.embedded import RRuntimeError
from pywps.app.exceptions import ProcessError
from pywps import Process, ComplexInput, LiteralInput, FORMATS, Format
from pywps.app.Common import Metadata

# PCIC libraries
from wps_tools import logging, R, io, error_handling
import chickadee.utils as util
import chickadee.io as chick_io


class Rerank(Process):
    """Quantile Reranking fixes bias introduced by the Climate Analogues
    step by re-applying a simple quantile mapping bias correction at
    each grid box"""

    def __init__(self):
        self.status_percentage_steps = dict(
            logging.common_status_percentages,
            **{"get_ClimDown": 5, "set_R_options": 10, "parallelization": 15},
        )

        self.handler_inputs = [
            chick_io.obs_file,
            chick_io.varname,
            chick_io.out_file,
            chick_io.num_cores,
            io.log_level,
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
                abstract="Rdata or RDS file containing the analogues produced from the CA step",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[Format("application/x-gzip", encoding="base64")],
            ),
            LiteralInput(
                "analogues_name",
                "Name of analogues R object",
                abstract="Name of the R object containing the analogues. You may leave as "
                "defualt for RDS files.",
                default="analogues",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
            ),
        ]
        inputs = self.handler_inputs + chick_io.general_options_input

        outputs = [io.nc_output]

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

    def read_analogues_file(sef, analogues, analogues_name):
        try:
            return R.load_rdata_to_python(analogues, analogues_name)
        except (RRuntimeError, ProcessError, IndexError):
            pass

        try:
            return robjects.r(f"readRDS('{analogues}')")
        except (RRuntimeError, ProcessError) as e:
            raise ProcessError(
                f"{type(e).__name__}: Analogues file must be a RDS file or "
                "a Rdata file containing an object of the given name"
            )

    def _handler(self, request, response):
        args = io.collect_args(request, self.workdir)
        (
            obs_file,
            varname,
            out_file,
            num_cores,
            loglevel,
            qdm_file,
            analogues_object,
            analogues_name,
        ) = util.select_args_from_input_list(args, self.handler_inputs)

        logging.log_handler(
            self,
            response,
            "Starting Process",
            util.logger,
            log_level=loglevel,
            process_step="start",
        )

        logging.log_handler(
            self,
            response,
            "Importing R package 'ClimDown'",
            util.logger,
            log_level=loglevel,
            process_step="get_ClimDown",
        )
        climdown = R.get_package("ClimDown")

        logging.log_handler(
            self,
            response,
            "Setting R options",
            util.logger,
            log_level=loglevel,
            process_step="set_R_options",
        )
        util.set_general_options(
            *util.select_args_from_input_list(args, chick_io.general_options_input)
        )

        logging.log_handler(
            self,
            response,
            "Setting parallelization",
            util.logger,
            log_level=loglevel,
            process_step="parallelization",
        )
        doPar = R.get_package("doParallel")
        doPar.registerDoParallel(cores=num_cores)

        logging.log_handler(
            self,
            response,
            "Applying quantile mapping bias correction",
            util.logger,
            log_level=loglevel,
            process_step="process",
        )

        analogues = self.read_analogues_file(analogues_object, analogues_name)

        try:
            climdown.rerank_netcdf_wrapper(
                qdm_file, obs_file, analogues, out_file, varname
            )
        except RRuntimeError as e:
            error_handling.custom_process_error(e)

        # Stop parallelization
        doPar.stopImplicitCluster()

        logging.log_handler(
            self,
            response,
            "Building final output",
            util.logger,
            log_level=loglevel,
            process_step="build_output",
        )

        response.outputs["output"].file = out_file

        # Clear R global env
        robjects.r("rm(list=ls())")

        logging.log_handler(
            self,
            response,
            "Process Complete",
            util.logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
