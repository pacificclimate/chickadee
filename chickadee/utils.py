import logging
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


def get_ClimDown():
    # Install and import R packages
    if not isinstalled("ClimDown"):
        utils = importr("utils")
        utils.chooseCRANmirror(ind=1)
        utils.install_packages("ClimDown")

    try:
        return importr("ClimDown")
    except PackageNotInstalledError:
        raise ProcessError("ClimDown isntallation has failed")


def get_doParallel():
    if not isinstalled("doParallel"):
        utils = importr("utils")
        utils.install_packages("doParallel")

    return importr("doParallel")
