from .wps_CA import CA
from .wps_CI import CI
from .wps_BCCAQ import BCCAQ
from .wps_QDM import QDM

processes = [
    CA(),
    CI(),
    BCCAQ(),
    QDM(),
]
