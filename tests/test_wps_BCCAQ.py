import pytest
from pkg_resources import resource_filename
from tempfile import NamedTemporaryFile
from datetime import date

from wps_tools.testing import run_wps_process
from chickadee.processes.wps_BCCAQ import BCCAQ


@pytest.mark.parametrize(
    ("gcm_file", "obs_file", "var", "end_date", "num_cores"),
    [
        (
            f"file://{resource_filename(__name__, 'data/tiny_gcm.nc')}",
            f"file://{resource_filename(__name__, 'data/tiny_obs.nc')}",
            "tasmax",
            date(1972, 12, 31),
            4,
        ),
    ],
)
def test_wps_bccaq(gcm_file, obs_file, var, end_date, num_cores):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = (
            f"gcm_file=@xlink:href={gcm_file};"
            f"obs_file=@xlink:href={obs_file};"
            f"varname={var};"
            f"end_date={end_date};"
            f"out_file={out_file.name};"
            f"num_cores={num_cores};"
        )
        run_wps_process(BCCAQ(), datainputs)