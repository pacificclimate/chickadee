import pytest
from pywps.app.exceptions import ProcessError
from pkg_resources import resource_filename
from chickadee.utils import get_package, collect_args, set_end_date
from datetime import date
from rpy2.robjects.packages import importr
from wps_tools.testing import run_wps_process
from .test_processes.wps_test_collect_args import TestCollectArgs

base = importr("base")


@pytest.mark.parametrize("package", ["ClimDown"])
def test_get_pacakge(package):
    pkg = get_package(package)
    assert pkg.__dict__["__rname__"] == package


@pytest.mark.parametrize("package", ["invalid_pkg"])
def test_get_package_err(package):
    with pytest.raises(ProcessError) as e:
        get_package(package)
    assert str(vars(e)["_excinfo"][1]) == f"R package, {package}, is not installed"


@pytest.mark.parametrize("end_date", [date(1972, 12, 31), date.today()])
def test_set_r_options(end_date):
    set_end_date(end_date)
    assert str(base.getOption("calibration.end")).split('"')[1].split()[0] == str(
        end_date
    )


@pytest.mark.parametrize(
    ("local_file", "opendap_url", "argc"),
    [
        (
            f"file://{resource_filename(__name__, 'data/tiny_gcm.nc')}",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/fileServer/datasets/storage/data/projects/comp_support/daccs/chickadee/tests/data/tiny_obs.nc",
            3,
        )
    ],
)
def test_collect_args(local_file, opendap_url, argc):
    params = (
        f"local_file=@xlink:href={local_file};"
        f"opendap_url=@xlink:href={opendap_url};"
        f"argc={argc};"
    )
    run_wps_process(TestCollectArgs(), params)
