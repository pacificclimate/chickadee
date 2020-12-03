import pytest
from pkg_resources import resource_filename
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process, local_path
from chickadee.processes.wps_rerank import Rerank


@pytest.mark.parametrize(
    ("obs_file", "var", "qdm_file", "analogues_object"),
    [
        (
            local_path("tiny_obs.nc"),
            "tasmax",
            local_path("QDM_expected_output.nc"),
            local_path("analogues.rda"),
        ),
    ],
)
def test_wps_rerank(obs_file, var, qdm_file, analogues_object):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = (
            f"obs_file=@xlink:href={obs_file};"
            f"varname={var};"
            f"out_file={out_file.name};"
            f"qdm_file=@xlink:href={qdm_file};"
            f"analogues_object=@xlink:href={analogues_object};"
        )
        run_wps_process(Rerank(), datainputs)
