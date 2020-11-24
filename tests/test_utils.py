import pytest
from pywps.app.exceptions import ProcessError
from pkg_resources import resource_filename
from chickadee.utils import (
    get_package,
    collect_args,
    set_general_options,
    set_ca_options,
    set_qdm_options,
)
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


@pytest.mark.parametrize(
    ("units_bool", "n_pr_bool", "tasmax_units", "tasmin_units", "pr_units", "max_gb"),
    [(False, False, "farenheit", "farenheit", "mm", 0.5)],
)
def test_set_general_options(
    units_bool,
    n_pr_bool,
    tasmax_units,
    tasmin_units,
    pr_units,
    max_gb,
):
    set_general_options(
        units_bool,
        n_pr_bool,
        tasmax_units,
        tasmin_units,
        pr_units,
        max_gb,
    )

    assert base.getOption("check.units")[0] == units_bool
    assert base.getOption("check.neg.precip")[0] == n_pr_bool
    assert list(base.getOption("target.units")) == [
        tasmax_units,
        tasmin_units,
        pr_units,
    ]
    assert base.getOption("max.GB")[0] == max_gb


@pytest.mark.parametrize(
    (
        "num_analogues",
        "delta_days",
        "start_date",
        "end_date",
        "trimmed_mean",
        "tol",
        "expon",
    ),
    [(25, 40.0, date(1996, 9, 14), date(2020, 11, 23), 0.5, 0.2, 0.6)],
)
def test_set_ca_options(
    num_analogues,
    delta_days,
    start_date,
    end_date,
    trimmed_mean,
    tol,
    expon,
):
    set_ca_options(
        num_analogues,
        delta_days,
        start_date,
        end_date,
        trimmed_mean,
        tol,
        expon,
    )

    assert base.getOption("n.analogues")[0] == num_analogues
    assert base.getOption("delta.days")[0] == delta_days
    assert str(base.getOption("calibration.start")).split('"')[1].split()[0] == str(
        start_date
    )
    assert str(base.getOption("calibration.end")).split('"')[1].split()[0] == str(
        end_date
    )
    assert base.getOption("trimmed.mean")[0] == trimmed_mean
    assert base.getOption("tol")[0] == tol
    assert base.getOption("expon")[0] == expon


@pytest.mark.parametrize(
    (
        "multiyear",
        "expand_multiyear",
        "multiyear_window_length",
        "trace",
        "jitter_factor",
        "pr_tau",
        "tasmax_tau",
        "tasmin_tau",
        "pr_seasonal",
        "tasmax_seasonal",
        "tasmin_seasonal",
        "pr_ratio",
        "tasmax_ratio",
        "tasmin_ratio",
    ),
    [
        (
            False,
            False,
            35,
            0.0025,
            0.02,
            1002,
            102,
            102,
            False,
            True,
            True,
            False,
            True,
            True,
        )
    ],
)
def test_set_qdm_options(
    multiyear,
    expand_multiyear,
    multiyear_window_length,
    trace,
    jitter_factor,
    pr_tau,
    tasmax_tau,
    tasmin_tau,
    pr_seasonal,
    tasmax_seasonal,
    tasmin_seasonal,
    pr_ratio,
    tasmax_ratio,
    tasmin_ratio,
):
    set_qdm_options(
        multiyear,
        expand_multiyear,
        multiyear_window_length,
        trace,
        jitter_factor,
        pr_tau,
        tasmax_tau,
        tasmin_tau,
        pr_seasonal,
        tasmax_seasonal,
        tasmin_seasonal,
        pr_ratio,
        tasmax_ratio,
        tasmin_ratio,
    )

    assert base.getOption("multiyear")[0] == multiyear
    assert base.getOption("expand.multiyear")[0] == expand_multiyear
    assert base.getOption("multiyear.window.length")[0] == multiyear_window_length
    assert base.getOption("trace")[0] == trace
    assert base.getOption("jitter.factor")[0] == jitter_factor
    assert [int(tau) for [tau] in list(base.getOption("tau"))] == [
        pr_tau,
        tasmax_tau,
        tasmin_tau,
    ]
    assert [bool(season[0]) for season in base.getOption("seasonal")] == [
        pr_seasonal,
        tasmax_seasonal,
        tasmin_seasonal,
    ]
    assert [bool(num[0]) for num in base.getOption("ratio")] == [
        pr_ratio,
        tasmax_ratio,
        tasmin_ratio,
    ]
