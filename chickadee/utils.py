import logging
from rpy2.robjects.packages import isinstalled, importr


logger = logging.getLogger("PYWPS")
logger.setLevel(logging.NOTSET)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: osprey: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_ClimDown():
    # Install and import R packages
    if not isinstalled("ClimDown"):
        utils = importr("utils")
        utils.install_packages("ClimDown")
    return importr("ClimDown")


def get_doParallel():
    if not isinstalled("doParallel"):
        utils = importr("utils")
        utils.install_packages("doParallel")

    return importr("doParallel")
