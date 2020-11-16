import logging
from rpy2.robjects.packages import isinstalled, importr
from rpy2.robjects.vectors import StrVector
from pywps.app.exceptions import ProcessError
from collections import OrderedDict


logger = logging.getLogger("PYWPS")
logger.setLevel(logging.NOTSET)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: chickadee: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_package(package):
    if isinstalled(package):
        return importr(package)
    else:
        raise ProcessError(f"R package, {package}, is not installed")


def collect_common_args(request):
    gcm_file = request.inputs["gcm_file"][0].file
    obs_file = request.inputs["obs_file"][0].file
    varname = request.inputs["varname"][0].data
    output_file = request.inputs["out_file"][0].data
    num_cores = request.inputs["num_cores"][0].data
    loglevel = request.inputs["loglevel"][0].data

    return gcm_file, obs_file, varname, output_file, num_cores, loglevel
