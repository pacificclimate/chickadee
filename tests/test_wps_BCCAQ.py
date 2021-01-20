import pytest
from pkg_resources import resource_filename
from tempfile import NamedTemporaryFile
from datetime import date

from wps_tools.testing import run_wps_process, local_path
from chickadee.processes.wps_BCCAQ import BCCAQ
from chickadee.utils import process_err_test


@pytest.mark.parametrize(
    ("gcm_file", "obs_file", "var", "end_date", "num_cores"),
    [
        (
            local_path("tiny_gcm.nc"),
            local_path("tiny_obs.nc"),
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


@pytest.mark.parametrize(
    ("gcm_file", "obs_file", "var", "end_date"),
    [
        (
            local_path("tiny_gcm.nc"),
            local_path("tiny_obs.nc"),
            "tx",
            date(1972, 12, 31),
        ),
        (
            local_path("tiny_gcm.nc"),
            local_path("tiny_gcm.nc"),
            "tasmax",
            date(1972, 12, 31),
        ),
        (
            local_path("tiny_gcm.nc"),
            local_path("tiny_obs.nc"),
            "tasmax",
            date(1, 1, 1),
        ),
    ],
)
def test_wps_bccaq_err(gcm_file, obs_file, var, end_date):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = (
            f"gcm_file=@xlink:href={gcm_file};"
            f"obs_file=@xlink:href={obs_file};"
            f"varname={var};"
            f"end_date={end_date};"
            f"out_file={out_file.name};"
        )
        process_err_test(BCCAQ, datainputs)
