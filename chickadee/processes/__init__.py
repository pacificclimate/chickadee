from .wps_ca import CA
from .wps_CI import CI
from .wps_bccaq import BCCAQ

processes = [
    CA(),
    CI(),
    BCCAQ(),
]
