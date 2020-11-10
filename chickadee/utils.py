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


def get_R_package(package):
    if not isinstalled(package):
        utils = importr("utils")
        utils.chooseCRANmirror(ind=1)
        utils.install_packages(package)

    try:
        return importr(package)
    except PackageNotInstalledError:
        raise ProcessError(f"{package} not installed")


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
