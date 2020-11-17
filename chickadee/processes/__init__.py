from .wps_CI import CI
from .wps_bccaq import BCCAQ
from .wps_QDM import QDM

processes = [
    CI(),
    BCCAQ(),
    QDM(),
]
