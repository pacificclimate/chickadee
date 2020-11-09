import pytest
import mock
import builtins
from pkg_resources import resource_filename
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process
from chickadee.processes.wps_CI import CI


@pytest.mark.parametrize(
    ("gcm_file", "obs_file", "varname"),
    [
        (
            f"file://{resource_filename(__name__, 'data/tiny_gcm.nc')}",
            f"file://{resource_filename(__name__, 'data/tiny_obs.nc')}",
            "tasmax",
        ),
    ],
)
def test_wps_CI(gcm_file, obs_file, varname):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = (
            f"gcm_file=@xlink:href={gcm_file};"
            f"obs_file=@xlink:href={obs_file};"
            f"varname={varname};"
            f"out_file={out_file.name};"
        )
        with mock.patch.object(builtins, "input", lambda _: "y"):
            run_wps_process(CI(), datainputs)
