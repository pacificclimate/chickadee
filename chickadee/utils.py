import logging
from rpy2 import robjects

logger = logging.getLogger("PYWPS")
logger.setLevel(logging.NOTSET)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: thunderbird: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

def set_r_options():
    robjects.r("""
    set_end_date <-function(end_date){
        options(
            calibration.end=as.POSIXct(end_date, tz='GMT')
        )
    }
    """)
    return robjects.r['set_end_date']