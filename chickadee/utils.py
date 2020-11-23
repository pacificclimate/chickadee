import logging
import os
from rpy2 import robjects
from rpy2.robjects.packages import isinstalled, importr
from pywps.app.exceptions import ProcessError
from collections import OrderedDict

logger = logging.getLogger("PYWPS")
logger.setLevel(logging.NOTSET)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: chickadee: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

common_status_percentage = {
    "start": 0,
    "process": 20,
    "build_output": 95,
    "complete": 100,
}


def get_package(package):
    if isinstalled(package):
        return importr(package)
    else:
        raise ProcessError(f"R package, {package}, is not installed")


def collect_args(request):
    args = OrderedDict()
    for k in request.inputs.keys():
        if "data_type" in vars(request.inputs[k][0]).keys():
            # LiteralData
            args[request.inputs[k][0].identifier] = request.inputs[k][0].data
        elif vars(request.inputs[k][0])["_url"] != None:
            # OPeNDAP
            args[request.inputs[k][0].identifier] = request.inputs[k][0].url
        elif os.path.isfile(request.inputs[k][0].file):
            # Local files
            args[request.inputs[k][0].identifier] = request.inputs[k][0].file

    return tuple(args.values())


def set_end_date(end_date):
    robjects.r(
        """
    set_end_date <-function(end_date){
        options(
            calibration.end=as.POSIXct(end_date, tz='GMT')
        )
    }
    """
    )

    robjects.r["set_end_date"](str(end_date))
    return


def set_general_options(
    units_bool,
    n_pr_bool,
    tasmax_units,
    tasmin_units,
    pr_units,
    max_gb,
):
    robjects.r(
        """
    function(max_gb, units_bool, n_pr_bool, tasmax_units, tasmin_units, pr_units){
        options(
            max.GB=max_gb,
            check.units=units_bool,
            check.neg.precip=n_pr_bool,
            target.units=c(tasmax=tasmax_units, tasmin=tasmin_units, pr=pr_units)
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
    )


def set_ca_options(
    num_analogues,
    delta_days,
    start_date,
    end_date,
    trimmed_mean,
    tol,
    expon,
):
    robjects.r(
        """
    function(trimmed_mean, delta_days, num_analogues, start_date, end_date, tol, expon){
        options(
            trimmed.mean=trimmed_mean,
            delta_days=delta_days,
            n.analogues=num_analogues,
            calibration.start=as.POSIXct(start_date, tz='GMT'),
            calibration.end=as.POSIXct(end_date, tz='GMT'),
            tol=tol,
            expon=expon
        )
    }
    """
    )(
        trimmed_mean,
        delta_days,
        num_analogues,
        str(start_date),
        str(end_date),
        tol,
        expon,
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
        tasmin_ratio
    )

