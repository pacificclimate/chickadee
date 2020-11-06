from pywps import Process, ComplexInput, ComplexOutput, LiteralInput, FORMATS
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

from wps_tools.utils import log_handler
from wps_tools.io import log_level
from chickadee.utils import logger, get_ClimDown, get_doParallel


class CI(Process):
    def __init__(self):
        self.status_percentage_steps = {
            "start": 0,
            "process": 10,
            "build_output": 95,
            "complete": 100,
        }
        inputs = [
            ComplexInput(
                "gcm_file",
                "GCM NetCDF file",
                abstract="Filename of GCM simulations",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            ComplexInput(
                "obs_file",
                "Observations NetCDF file",
                abstract="Filename of high-res gridded historical observations",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            LiteralInput(
                "varname",
                "Variable to Downscale",
                abstract="Name of the NetCDF variable to downscale (e.g. 'tasmax')",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
            ),
            LiteralInput(
                "out_file",
                "Output NetCDF File",
                abstract="Filename to create with the climate imprint outputs",
                min_occurs=0,
                max_occurs=1,
                data_type="string",
            ),
            log_level,
        ]

        outputs = [
            ComplexOutput(
                "output",
                "Output",
                abstract="output netCDF file",
                supported_formats=[FORMATS.NETCDF],
            ),
        ]

        super(CI, self).__init__(
            self._handler,
            identifier="ci",
            title="CI",
            abstract="Climate Imprint (CI) downscaling",
            metadata=[
                Metadata("NetCDF processing"),
                Metadata("Climate Data Operations"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    def collect_args(self, request):
        loglevel = request.inputs["loglevel"][0].data
        gcm_file = request.inputs["gcm_file"][0].file
        obs_file = request.inputs["obs_file"][0].file
        varname = request.inputs["varname"][0].data
        output_file = request.inputs["out_file"][0].data

        return loglevel, gcm_file, obs_file, varname, output_file

    def _handler(self, request, response):
        loglevel, gcm_file, obs_file, varname, output_file = self.collect_args(request)
        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        climdown = get_ClimDown()

        log_handler(
            self,
            response,
            "Processing CI downscaling",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        # Set parallelization
        doPar = get_doParallel()
        doPar.registerDoParallel(cores=4)

        climdown.ci_netcdf_wrapper(gcm_file, obs_file, output_file, varname)

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
