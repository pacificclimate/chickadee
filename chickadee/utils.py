import logging
from rpy2.robjects.packages import isinstalled, importr
from rpy2.robjects.vectors import StrVector
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
    if isinstalled("ClimDown"):
        return importr("ClimDown")
    else:
        raise ProcessError(f"R package, {package}, is not installed")


def get_doParallel():
    if not isinstalled("doParallel"):
        utils = importr("utils")
        utils.install_packages("doParallel")

    return importr("doParallel")
