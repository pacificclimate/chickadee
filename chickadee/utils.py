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
    selected_args = []
    for input_ in inputs:
        # OPeNDAP URLs
        if input_.identifier in ["gcm_file", "obs_file"]:
            value = args[input_.identifier][0].reference
        else:
            value = (
                args[input_.identifier][0].data
                if hasattr(args[input_.identifier][0], "data")
                else args[input_.identifier]
            )
        selected_args.append(value)
    return tuple(selected_args)


def r_boolean(python_bool):
    bool_string = "TRUE" if python_bool else "FALSE"
    return bool_string


def set_general_options(
    units_bool,
    n_pr_bool,
    tasmax_units,
    tasmin_units,
    tg_units,
    pr_units,
    max_gb,
    start_date,
    end_date,
):
    robjects.r(
        f"""
        options(
            max.GB={max_gb},
            check.units={r_boolean(units_bool)},
            check.neg.precip={r_boolean(n_pr_bool)},
            target.units=c(tasmax='{tasmax_units}', tasmin='{tasmin_units}', tg='{tg_units}', pr='{pr_units}'),
            calibration.start=as.POSIXct('{start_date}', tz='GMT'),
            calibration.end=as.POSIXct('{end_date}', tz='GMT')
        )
        """
    )


def set_ca_options(
    num_analogues,
    delta_days,
    trimmed_mean,
    tol,
):
    robjects.r(
        f"""
        options(
            trimmed.mean={trimmed_mean},
            delta.days={delta_days},
            n.analogues={num_analogues},
            tol={tol}
        )
        """
    )


def set_ci_options(
    gcm_varname,
    obs_varname,
):
    robjects.r(
        f"""
        options(
            gcm.varname='{gcm_varname}',
            obs.varname='{obs_varname}'
        )
        """
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
        f"""
        options(
            multiyear={r_boolean(multiyear)},
            expand.multiyear={r_boolean(expand_multiyear)},
            multiyear.window.length={multiyear_window_length},
            trace={trace},
            jitter.factor={jitter_factor},
            tau=list(pr={pr_tau}, tasmax={tasmax_tau}, tasmin={tasmin_tau}),
            seasonal=list(pr={r_boolean(pr_seasonal)}, tasmax={r_boolean(tasmax_seasonal)}, tasmin={r_boolean(tasmin_seasonal)}),
            ratio=list(pr={r_boolean(pr_ratio)}, tasmax={r_boolean(tasmax_ratio)}, tasmin={r_boolean(tasmin_ratio)})
        )
        """
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
