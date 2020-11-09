import logging
from rpy2 import robjects
from rpy2.robjects.packages import isinstalled, importr, PackageNotInstalledError, InstalledPackages
from pywps.app.exceptions import ProcessError

logger = logging.getLogger("PYWPS")
logger.setLevel(logging.NOTSET)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: chickadee: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_R_package(repo, package_name, version):
    # Install and import an R package
    if not isinstalled(package_name):
        utils = importr("utils")
        utils.chooseCRANmirror(ind=1)

        if not isinstalled("devtools"):
            utils.install_packages("devtools")

        devtools = importr("devtools")
        devtools.install_github(f"{repo}/{package_name}", ref=version)

    try:
        return importr(package_name)
    except PackageNotInstalledError:
        raise ProcessError(f"{package_name} not installed")


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
