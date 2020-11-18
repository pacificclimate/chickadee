import pytest
from pkg_resources import resource_filename
from tempfile import NamedTemporaryFile
from datetime import date

from wps_tools.testing import run_wps_process
from chickadee.processes.wps_ca import CA


@pytest.mark.parametrize(
    (
        "gcm_file",
        "obs_file",
        "var",
        "end_date",
        "num_cores",
        "indices",
        "weights",
    ),
    [
        (
            f"file://{resource_filename(__name__, 'data/tiny_gcm.nc')}",
            f"file://{resource_filename(__name__, 'data/tiny_obs.nc')}",
            "tasmax",
            date(1972, 12, 31),
            4,
            "indices.txt",
            "weights.txt",
        ),
    ],
)
def test_wps_ca(gcm_file, obs_file, var, end_date, num_cores, indices, weights):
    datainputs = (
        f"gcm_file=@xlink:href={gcm_file};"
        f"obs_file=@xlink:href={obs_file};"
        f"varname={var};"
        f"end_date={end_date};"
        f"num_cores={num_cores};"
        f"indices={indices};"
        f"weights={weights};"
    )
    run_wps_process(CA(), datainputs)
