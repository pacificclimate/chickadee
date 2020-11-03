import pytest
from pkg_resources import resource_filename
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process
from chickadee.processes.wps_bccaq import BCCAQ


@pytest.mark.parametrize(
    ("gcm_file", "obs_file", "var", "end_date", "out_file"),
    [
        (
            resource_filename("tests", "data/tiny_gcm.nc"),
            resource_filename("tests", "data/tiny_obs.nc"),
            "tasmax",
            "1972-12-31",
            NamedTemporaryFile(suffix=".nc", prefix="output_", dir="/tmp", delete=True),
        ),
    ],
)
def test_wps_bccaq(gcm_file, obs_file, var, end_date, out_file):
    datainputs = (
        f"gcm_file={gcm_file};"
        f"obs_file={obs_file};"
        f"var={var};"
        f"end_date={end_date};"
        f"out_file={out_file.name};"
    )
    run_wps_process(BCCAQ(), datainputs)
    out_file.close()
