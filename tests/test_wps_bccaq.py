import pytest
from pkg_resources import resource_filename
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process
from chickadee.processes.wps_bccaq import BCCAQ


@pytest.mark.slow
@pytest.mark.parametrize(
    ("gcm_file", "obs_file", "var", "end_date", "out_file"),
    [
        (
            f"file://{resource_filename(__name__, 'data/tiny_gcm.nc')}",
            f"file://{resource_filename(__name__, 'data/tiny_obs.nc')}",
            "tasmax",
            "1972-12-31",
            NamedTemporaryFile(suffix=".nc", prefix="output_", dir="/tmp", delete=True),
        ),
    ],
)
def test_wps_bccaq(gcm_file, obs_file, var, end_date, out_file):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = (
            f"gcm_file=@xlink:href={gcm_file};"
            f"obs_file=@xlink:href={obs_file};"
            f"var={var};"
            f"end_date={end_date};"
            f"out_file={out_file.name};"
        )
        run_wps_process(BCCAQ(), datainputs)
