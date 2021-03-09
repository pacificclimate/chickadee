import pytest
import io
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process, local_path, url_path, process_err_test
from chickadee.processes.wps_CI import CI


def build_params(gcm_file, obs_file, var, out_file):
    return (
        f"gcm_file=@xlink:href={gcm_file};"
        f"obs_file=@xlink:href={obs_file};"
        f"varname={var};"
        f"out_file={out_file};"
    )


@pytest.mark.parametrize(
    ("gcm_file", "obs_file", "varname"),
    [
        (
            local_path("tiny_gcm.nc"),
            local_path("tiny_obs.nc"),
            "tasmax",
        ),
    ],
)
def test_wps_CI_local(gcm_file, obs_file, varname, monkeypatch):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = build_params(gcm_file, obs_file, varname, out_file.name)
        monkeypatch.setattr("sys.stdin", io.StringIO("No"))
        run_wps_process(CI(), datainputs)


@pytest.mark.online
@pytest.mark.parametrize(
    ("gcm_file", "obs_file", "varname"),
    [
        (
            local_path("tiny_gcm.nc"),
            url_path("tiny_obs.nc", "opendap"),
            "tasmax",
        ),
    ],
)
def test_wps_CI_online(gcm_file, obs_file, varname, monkeypatch):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = build_params(gcm_file, obs_file, varname, out_file.name)
        monkeypatch.setattr("sys.stdin", io.StringIO("No"))
        run_wps_process(CI(), datainputs)


@pytest.mark.parametrize(
    ("gcm_file", "obs_file", "varname"),
    [
        (local_path("tiny_gcm.nc"), local_path("tiny_obs.nc"), "tx"),
        (
            local_path("tiny_gcm.nc"),
            local_path("tiny_gcm.nc"),
            "tasmax",
        ),
    ],
)
def test_wps_CI_err(gcm_file, obs_file, varname, monkeypatch):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = build_params(gcm_file, obs_file, varname, out_file.name)
        monkeypatch.setattr("sys.stdin", io.StringIO("No"))
        process_err_test(CI, datainputs)
