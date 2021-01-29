import pytest
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process, local_path, process_err_test
from chickadee.processes.wps_QDM import QDM


@pytest.mark.parametrize(
    ("gcm_file", "obs_file", "var", "num_cores"),
    [
        (
            local_path("CI_expected_output.nc"),
            local_path("tiny_obs.nc"),
            "tasmax",
            4,
        ),
    ],
)
def test_wps_QDM(obs_file, gcm_file, var, num_cores):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = (
            f"obs_file=@xlink:href={obs_file};"
            f"gcm_file=@xlink:href={gcm_file};"
            f"varname={var};"
            f"out_file={out_file.name};"
            f"num_cores={num_cores};"
        )
        run_wps_process(QDM(), datainputs)


@pytest.mark.parametrize(
    ("gcm_file", "obs_file", "var"),
    [
        (
            local_path("CI_expected_output.nc"),
            local_path("tiny_obs.nc"),
            "tx",
        ),
    ],
)
def test_wps_QDM_err(obs_file, gcm_file, var):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = (
            f"obs_file=@xlink:href={obs_file};"
            f"gcm_file=@xlink:href={gcm_file};"
            f"varname={var};"
            f"out_file={out_file.name};"
        )
        process_err_test(QDM, datainputs)
