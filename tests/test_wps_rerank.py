import pytest
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process, local_path, process_err_test
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


@pytest.mark.parametrize(
    ("obs_file", "var", "qdm_file", "analogues_object", "analogues_name"),
    [
        (
            local_path("tiny_obs.nc"),
            "tasmax",
            local_path("QDM_expected_output.nc"),
            local_path("analogues.rda"),
            "not_analogues",
        ),
        (
            local_path("tiny_obs.nc"),
            "tx",
            local_path("QDM_expected_output.nc"),
            local_path("analogues.rda"),
            "analogues",
        ),
    ],
)
def test_wps_rerank_err(obs_file, var, qdm_file, analogues_object, analogues_name):
    with NamedTemporaryFile(
        suffix=".nc", prefix="output_", dir="/tmp", delete=True
    ) as out_file:
        datainputs = (
            f"obs_file=@xlink:href={obs_file};"
            f"varname={var};"
            f"out_file={out_file.name};"
            f"qdm_file=@xlink:href={qdm_file};"
            f"analogues_name={analogues_name};"
            f"analogues_object=@xlink:href={analogues_object};"
        )
        process_err_test(Rerank, datainputs)
