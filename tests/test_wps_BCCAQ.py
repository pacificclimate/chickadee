import pytest
from tempfile import NamedTemporaryFile
from datetime import date

from wps_tools.testing import run_wps_process, local_path, process_err_test, url_path
from chickadee.processes.wps_BCCAQ import BCCAQ


def build_params(gcm_file, obs_file, var, end_date, num_cores, out_file):
    return (
        f"gcm_file=@xlink:href={gcm_file};"
        f"obs_file=@xlink:href={obs_file};"
        f"varname={var};"
        f"end_date={end_date};"
        f"out_file={out_file};"
        f"num_cores={num_cores};"
    )


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
def test_wps_bccaq_local(gcm_file, obs_file, var, end_date, num_cores):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = build_params(
            gcm_file, obs_file, var, end_date, num_cores, out_file.name
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
@pytest.mark.parametrize(("num_cores"), [4])
def test_wps_bccaq_err(gcm_file, obs_file, var, end_date, num_cores):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = build_params(
            gcm_file, obs_file, var, end_date, num_cores, out_file.name
        )
        process_err_test(BCCAQ, datainputs)
