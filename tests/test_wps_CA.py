import pytest
from pkg_resources import resource_filename
from tempfile import NamedTemporaryFile
from datetime import date

from wps_tools.testing import run_wps_process, local_path
from chickadee.processes.wps_CA import CA


@pytest.mark.parametrize(
    (
        "gcm_file",
        "obs_file",
        "var",
        "end_date",
    ),
    [
        (
            local_path("tiny_gcm.nc"),
            local_path("tiny_obs.nc"),
            "tasmax",
            date(1972, 12, 31),
        ),
    ],
)
def test_wps_ca(gcm_file, obs_file, var, end_date):
    with NamedTemporaryFile(
        suffix=".txt", prefix="indices_", dir="/tmp", delete=True
    ) as output_file:
        datainputs = (
            f"gcm_file=@xlink:href={gcm_file};"
            f"obs_file=@xlink:href={obs_file};"
            f"varname={var};"
            f"end_date={end_date};"
            f"output_file={output_file.name};"
        )
    run_wps_process(CA(), datainputs)
