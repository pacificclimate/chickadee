from pywps import Process, ComplexInput, ComplexOutput, LiteralInput, FORMATS
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

from wps_tools.utils import log_handler
from wps_tools.io import log_level
from chickadee.utils import logger, get_ClimDown


class CI(Process):
    def __init__(self):
        self.status_percentage_steps = {
            "start": 0,
            "process": 10,
            "build_output": 95,
            "complete": 100,
        }
        inputs = [
            log_level,
            ComplexInput(
                "gcm_file",
                "GCM NetCDF file",
                abstract="Filename of GCM simulations",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF],
            ),
            ComplexInput(
                "obs_file",
                "Observations NetCDF file",
                abstract="Filename of high-res gridded historical observations",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF],
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
                "out_file_create",
                "Output NetCDF File",
                abstract="Filename to create with the climate imprint outputs",
                min_occurs=0,
                max_occurs=1,
                data_type="string",
            ),
            ComplexInput(
                "out_file_overwrite",
                "Output NetCDF File",
                abstract="Filename to overwrite with the climate imprint outputs",
                min_occurs=0,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF],
            ),
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
        gcm_file = request.inputs["gcm_file"][0].file
        obs_file = request.inputs["obs_file"][0].file
        varname = request.inputs["varname"][0].data
        if "out_file_create" in request.inputs.keys():
            output_file = request.inputs["out_file_create"][0].data
        elif "out_file_overwrite" in request.inputs.keys():
            output_file = request.inputs["out_file_overwrite"][0].file
        else:
            ProcessError("out_file argument not provided")

        return gcm_file, obs_file, varname, output_file

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

        gcm_file, obs_file, varname, output_file = self.collect_args(request)

        climdown = get_ClimDown()

        climdown.ci_netcdf_wrapper(gcm_file, obs_file, output_file, varname)

        response.outputs["output"].file = output_file

        return response
