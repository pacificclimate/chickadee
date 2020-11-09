import logging
from rpy2.robjects.packages import isinstalled, importr, PackageNotInstalledError
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


def get_ClimDown(package, version):
    # Install and import R packages
    if not isinstalled("ClimDown"):
        utils = importr("utils")
        base = importr("base")
        utils.install_packages(
            f"https://cloud.r-project.org/src/contrib/{package}_{version}.tar.gz",
            lib=base._libPaths()[0],
        )

    try:
        return importr("ClimDown")
    except PackageNotInstalledError:
        raise ProcessError("ClimDown installation has failed")


def get_doParallel():
    if not isinstalled("doParallel"):
        utils = importr("utils")
        utils.install_packages("doParallel")

    return importr("doParallel")
