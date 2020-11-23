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
