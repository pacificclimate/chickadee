import pytest
from pkg_resources import resource_filename
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process
from chickadee.processes.wps_rerank import Rerank


@pytest.mark.parametrize(
    ("obs_file", "var", "num_cores", "qdm_file", "analogues_object"),
    [
        (
            f"file://{resource_filename(__name__, 'data/tiny_obs.nc')}",
            "tasmax",
            4,
            f"file://{resource_filename(__name__, 'data/QDM_expected_output.nc')}",
            resource_filename(__name__, "data/analogues.rds"),
        ),
    ],
)
def test_wps_rerank(obs_file, var, num_cores, qdm_file, analogues_object):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = (
            f"obs_file=@xlink:href={obs_file};"
            f"varname={var};"
            f"out_file={out_file.name};"
            f"num_cores={num_cores};"
            f"qdm_file=@xlink:href={qdm_file};"
            f"analogues_object={analogues_object};"
        )
        run_wps_process(Rerank(), datainputs)
