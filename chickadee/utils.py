import logging
from rpy2 import robjects
from rpy2.robjects.packages import isinstalled, importr
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

common_status_percentage = {
    "start": 0,
    "process": 20,
    "build_output": 95,
    "complete": 100,
}


def get_package(package):
    if isinstalled(package):
        return importr(package)
    else:
        raise ProcessError(f"R package, {package}, is not installed")


def collect_args(request):
    args = OrderedDict()
    for k in request.inputs.keys():
        if "data_type" in vars(request.inputs[k][0]).keys():
            # LiteralData
            args[request.inputs[k][0].identifier] = request.inputs[k][0].data
        elif vars(request.inputs[k][0])["_url"] != None:
            # OPeNDAP
            args[request.inputs[k][0].identifier] = request.inputs[k][0].url
        elif vars(request.inputs[k][0])["_file"] != None:
            # Local files
            args[request.inputs[k][0].identifier] = request.inputs[k][0].file

    return tuple(args.values())


def set_end_date(end_date):
    robjects.r(
        """
    set_end_date <-function(end_date){
        options(
            calibration.end=as.POSIXct(end_date, tz='GMT')
        )
    }
    """
    )

    robjects.r["set_end_date"](str(end_date))
    return
