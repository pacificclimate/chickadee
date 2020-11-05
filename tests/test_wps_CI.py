import pytest
from pkg_resources import resource_filename
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process
from chickadee.processes.wps_CI import CI


@pytest.mark.online
@pytest.mark.parametrize(
    ("gcm_file", "obs_file", "varname", "out_file"),
    [
        (
            f"file://{resource_filename(__name__, 'data/tiny_gcm.nc')}",
            f"file://{resource_filename(__name__, 'data/tiny_obs.nc')}",
            "tasmax",
            NamedTemporaryFile(suffix=".nc", prefix="output_", dir="/tmp", delete=True),
        ),
    ],
)
def test_wps_CI(gcm_file, obs_file, varname, out_file):
    datainputs = (
        f"gcm_file=@xlink:href={gcm_file};"
        f"obs_file=@xlink:href={obs_file};"
        f"varname={varname};"
        f"out_file_create={out_file.name};"
    )
    run_wps_process(CI(), datainputs)
    out_file.close()
