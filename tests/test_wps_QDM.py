import pytest
from pkg_resources import resource_filename
from tempfile import NamedTemporaryFile
from datetime import date

from wps_tools.testing import run_wps_process, local_path
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
