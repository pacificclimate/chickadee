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


def install_R_package(package, version):
    if not isinstalled(package):
        utils = importr("utils")
        utils.chooseCRANmirror(ind=1)
        utils.install_packages(
            f"https://cloud.r-project.org/src/contrib/{package}_{version}.tar.gz",
        )


def get_R_package(package, version):
    try:
        return importr(package)
    except PackageNotInstalledError:
        raise ProcessError(f"{package} not installed")


def get_doParallel():
    required_packages = [
        ("iterators", "1.0.13"),
        ("foreach", "1.5.1"),
        ("doParallel", "1.0.16"),
    ]

    for package, version in required_packages:
        get_R_package(package, version)

    return get_R_package("doParallel", "1.0.16")


def get_climdown():
    package = "ClimDown"
    version = "1.0.7"

    install_R_package(package, version)
    return get_R_package(package, version)


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
