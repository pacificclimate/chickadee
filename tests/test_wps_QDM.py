import pytest
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process, local_path, url_path, process_err_test
from chickadee.processes.wps_QDM import QDM


def build_params(gcm_file, obs_file, var, out_file):
    return (
        f"gcm_file=@xlink:href={gcm_file};"
        f"obs_file=@xlink:href={obs_file};"
        f"varname={var};"
        f"out_file={out_file};"
    )


@pytest.mark.parametrize(
    ("gcm_file", "obs_file", "var"),
    [(local_path("CI_expected_output.nc"), local_path("tiny_obs.nc"), "tasmax",),],
)
def test_wps_QDM_local(obs_file, gcm_file, var):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = build_params(gcm_file, obs_file, var, out_file.name)
        run_wps_process(QDM(), datainputs)


@pytest.mark.online
@pytest.mark.parametrize(
    ("gcm_file", "obs_file", "var"),
    [
        (
            local_path("CI_expected_output.nc"),
            url_path("tiny_obs.nc", "opendap"),
            "tasmax",
        ),
    ],
)
def test_wps_QDM_online(obs_file, gcm_file, var):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = build_params(gcm_file, obs_file, var, out_file.name)
        run_wps_process(QDM(), datainputs)


@pytest.mark.parametrize(
    ("gcm_file", "obs_file", "var"),
    [(local_path("CI_expected_output.nc"), local_path("tiny_obs.nc"), "tx",),],
)
def test_wps_QDM_err(obs_file, gcm_file, var):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = build_params(gcm_file, obs_file, var, out_file.name)
        process_err_test(QDM, datainputs)
