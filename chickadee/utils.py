import pytest, logging, io, re
from rpy2 import robjects
from tempfile import NamedTemporaryFile
from urllib.request import urlretrieve
from pkg_resources import resource_filename
from pywps.app.exceptions import ProcessError
from contextlib import redirect_stderr

from wps_tools.testing import run_wps_process


logger = logging.getLogger("PYWPS")
logger.setLevel(logging.NOTSET)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: chickadee: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def select_args_from_input_list(args, inputs):
    return (args[input_.identifier][0] for input_ in inputs)


def set_general_options(
    units_bool,
    n_pr_bool,
    tasmax_units,
    tasmin_units,
    pr_units,
    max_gb,
    start_date,
    end_date,
):
    robjects.r(
        """
    function(max_gb, units_bool, n_pr_bool, tasmax_units, tasmin_units, pr_units, start_date, end_date){
        options(
            max.GB=max_gb,
            check.units=units_bool,
            check.neg.precip=n_pr_bool,
            target.units=c(tasmax=tasmax_units, tasmin=tasmin_units, pr=pr_units),
            calibration.start=as.POSIXct(start_date, tz='GMT'),
            calibration.end=as.POSIXct(end_date, tz='GMT')
        )
    }
    """
    )(
        max_gb,
        units_bool,
        n_pr_bool,
        tasmax_units,
        tasmin_units,
        pr_units,
        str(start_date),
        str(end_date),
    )


def set_ca_options(
    num_analogues, delta_days, trimmed_mean, tol,
):
    robjects.r(
        """
    function(trimmed_mean, delta_days, num_analogues, tol){
        options(
            trimmed.mean=trimmed_mean,
            delta.days=delta_days,
            n.analogues=num_analogues,
            tol=tol
        )
    }
    """
    )(
        trimmed_mean, delta_days, num_analogues, tol,
    )


def set_qdm_options(
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
    robjects.r(
        """
    function(
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
        tasmin_ratio
    ){
        options(
            multiyear=multiyear,
            expand.multiyear=expand_multiyear,
            multiyear.window.length=multiyear_window_length,
            trace=trace,
            jitter.factor=jitter_factor,
            tau=list(pr=pr_tau, tasmax=tasmax_tau, tasmin=tasmin_tau),
            seasonal=list(pr=pr_seasonal, tasmax=tasmax_seasonal, tasmin=tasmin_seasonal),
            ratio=list(pr=pr_ratio, tasmax=tasmax_ratio, tasmin=tasmin_ratio)
        )
    }
    """
    )(
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


def test_analogues(url, analogues_name, expected_file, expected_analogues):
    with NamedTemporaryFile(
        suffix=".rda", prefix="tmp_copy", dir="/tmp", delete=True
    ) as tmp_file:
        urlretrieve(url, tmp_file.name)
        robjects.r(f"load(file='{tmp_file.name}')")

    robjects.r(
        "load(file='{}')".format(resource_filename("tests", f"data/{expected_file}"))
    )

    for col in ["indices", "weights"]:
        r_expected = f'{expected_analogues}[["{col}"]]'
        r_output = f'{analogues_name}[["{col}"]]'

        expected_vector = robjects.r(r_expected)

        for i in range(1, len(expected_vector) + 1):
            test = f"all({r_expected}[[{i}]]=={r_output}[[{i}]])"

            assert robjects.r(test)

    # Clear R global env
    robjects.r("rm(list=ls())")
