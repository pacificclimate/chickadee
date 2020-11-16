import logging
from rpy2 import robjects
from rpy2.robjects.packages import isinstalled, importr, PackageNotInstalledError
from pywps.app.exceptions import ProcessError

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
