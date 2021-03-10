import pytest
from tempfile import NamedTemporaryFile
from datetime import date

from wps_tools.testing import run_wps_process, local_path, url_path, process_err_test
from chickadee.processes.wps_CA import CA


def build_params(gcm_file, obs_file, var, end_date, out_file):
    return (
        f"gcm_file=@xlink:href={gcm_file};"
        f"obs_file=@xlink:href={obs_file};"
        f"varname={var};"
        f"end_date={end_date};"
        f"out_file={out_file};"
    )


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
def test_wps_ca_local(gcm_file, obs_file, var, end_date):
    with NamedTemporaryFile(
        suffix=".txt", prefix="indices_", dir="/tmp", delete=True
    ) as output_file:
        datainputs = build_params(gcm_file, obs_file, var, end_date, output_file.name)

        run_wps_process(CA(), datainputs)


@pytest.mark.online
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
            url_path("tiny_obs.nc", "opendap"),
            "tasmax",
            date(1972, 12, 31),
        ),
    ],
)
def test_wps_ca_online(gcm_file, obs_file, var, end_date):
    with NamedTemporaryFile(
        suffix=".txt", prefix="indices_", dir="/tmp", delete=True
    ) as output_file:
        datainputs = build_params(gcm_file, obs_file, var, end_date, output_file.name)

        run_wps_process(CA(), datainputs)


@pytest.mark.parametrize(
    ("var", "end_date", "vector_name"),
    [
        (
            "tx",
            date(1972, 12, 31),
            "vector_name",
        ),
        (
            "tasmax",
            date(1, 1, 1),
            "vector_name",
        ),
        (
            "tasmax",
            date(1972, 12, 31),
            "vector name",
        ),
    ],
)
@pytest.mark.parametrize(
    ("gcm_file", "obs_file"),
    [
        (local_path("tiny_gcm.nc"), local_path("tiny_obs.nc")),
    ],
)
def test_wps_ca_err(gcm_file, obs_file, var, end_date, vector_name):
    with NamedTemporaryFile(
        suffix=".txt", prefix="indices_", dir="/tmp", delete=True
    ) as output_file:
        datainputs = (
            build_params(gcm_file, obs_file, var, end_date, output_file.name)
            + f"vector_name={vector_name};"
        )
        process_err_test(CA, datainputs)
