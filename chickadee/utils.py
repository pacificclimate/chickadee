import logging
import os
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
        elif os.path.isfile(request.inputs[k][0].file):
            # Local files
            args[request.inputs[k][0].identifier] = request.inputs[k][0].file

    return tuple(args.values())


def set_r_options(
    num_analogues=30,
    start_date='1971-01-01',
    end_date='2005-12-31',
    units_bool=True,
    n_pr_bool=True,
    tasmax_units='celsius',
    tasmin_units='celsius',
    pr_units='kg m-2 d-1'
):
    robjects.r(
        """
    function(num_analogues, start_date, end_date, units_bool, n_pr_bool, tasmax_units, tasmin_units, pr_units){
        options(
            n.analogues=num_analogues,
            calibration.end=as.POSIXct(start_date, tz='GMT'),
            calibration.end=as.POSIXct(end_date, tz='GMT'),
            check.units=units_bool,
            check.neg.precip=n_pr_bool,
            target.units=c(tasmax=tasmax_units, tasmin=tasmin_units, pr=pr_units)
        )
    }
    """
    )

    robjects.r["set_end_date"](num_analogues, str(start_date), str(end_date), units_bool, n_pr_bool, tasmax_units, tasmin_units, pr_units)
    return
