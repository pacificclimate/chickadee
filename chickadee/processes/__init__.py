from .wps_CA import CA
from .wps_CI import CI
from .wps_BCCAQ import BCCAQ
from .wps_QDM import QDM
from .wps_rerank import Rerank
from .wps_cancel import CancelProcess

processes = [
    CA(),
    CI(),
    BCCAQ(),
    QDM(),
    Rerank(),
    CancelProcess(),
]
