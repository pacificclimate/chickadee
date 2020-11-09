import logging
from rpy2 import robjects
from rpy2.robjects.packages import isinstalled, importr

logger = logging.getLogger("PYWPS")
logger.setLevel(logging.NOTSET)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: chickadee: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_R_package(package_name, version):
    # Install and import an R package
    if not isinstalled(package_name):
        utils = importr("utils")
        utils.chooseCRANmirror(ind=1)
        utils.install_packages(
            f"https://cloud.r-project.org/src/contrib/{package_name}_{version}.tar.gz"
        )

    return importr(package_name)


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
