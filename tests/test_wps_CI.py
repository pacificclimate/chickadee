import pytest
import io
from pkg_resources import resource_filename
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process, local_path
from chickadee.processes.wps_CI import CI


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
def test_wps_CI(gcm_file, obs_file, varname, monkeypatch):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = (
            f"gcm_file=@xlink:href={gcm_file};"
            f"obs_file=@xlink:href={obs_file};"
            f"varname={varname};"
            f"out_file={out_file.name};"
        )
        monkeypatch.setattr("sys.stdin", io.StringIO("No"))
        run_wps_process(CI(), datainputs)
