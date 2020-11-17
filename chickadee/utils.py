import logging
from rpy2 import robjects
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
    return_args = [
        request.inputs["gcm_file"][0].file,
        request.inputs["obs_file"][0].file,
        request.inputs["varname"][0].data,
        request.inputs["out_file"][0].data,
        request.inputs["num_cores"][0].data,
    ]
    if "end_date" in request.inputs.keys():
        return_args.append(str(request.inputs["end_date"][0].data))
    return_args.append(request.inputs["loglevel"][0].data)

    print(return_args)
    return tuple(return_args)


def set_r_options():
    robjects.r(
        """
    set_end_date <-function(end_date){
        options(
            calibration.end=as.POSIXct(end_date, tz='GMT')
        )
    }
    """
    )
    return robjects.r["set_end_date"]
