import pytest, logging, io, re
from rpy2 import robjects
from rpy2.rinterface_lib import callbacks
from tempfile import NamedTemporaryFile
from urllib.request import urlretrieve
from pkg_resources import resource_filename
from pywps.response.status import WPS_STATUS
from pywps.app.exceptions import ProcessError
from contextlib import redirect_stderr
from pywps.dblog import get_session, ProcessInstance
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
    return (args[input_.identifier] for input_ in inputs)


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


def raise_if_failed(response):
    # Check in-memory response status
    if response.status == WPS_STATUS.FAILED:
        raise ProcessError("Process failed.")

    uuid = response.uuid

    session = get_session()
    try:
        process = session.query(ProcessInstance).filter_by(uuid=uuid).first()
        if process and process.status == WPS_STATUS.FAILED:
            response.update_status(WPS_STATUS.FAILED, "Process failed.", 100)
            response.clean()
            raise ProcessError("Process failed.")
    finally:
        session.close()


def update_status_with_check(response, message, percentage):
    session = get_session()
    try:
        process = session.query(ProcessInstance).filter_by(uuid=response.uuid).first()
        if process and process.status == WPS_STATUS.FAILED:
            response.update_status(WPS_STATUS.FAILED, message, percentage)
        else:
            response.update_status(message, percentage)
    finally:
        session.close()


# Using Rpy2 callbacks to monitor process progress.
# See https://rpy2.github.io/doc/latest/html/callbacks.html#write-console
def create_r_progress_monitor(process_instance, response, logger, log_level):
    original_console_write = callbacks.consolewrite_print

    progress_markers = {
        "Calculating daily anomalies on the GCM": 23,
        "Creating cache file for the interpolated GCM": 26,
        "Interpolating the GCM daily anomalies to observation grid": 29,
        "Check observations file": 58,
        "Reading the monthly climatologies from the observations": 61,
        "Calculating the monthly factor across the GCM time series": 64,
        "Adding the monthly climatologies to the interpolated GCM": 67,
    }

    # Callback to capture R console output and update progress
    def custom_console_write(text):
        original_console_write(text)

        session = get_session()
        try:
            process = (
                session.query(ProcessInstance).filter_by(uuid=response.uuid).first()
            )
            if process and process.status == WPS_STATUS.FAILED:
                logger.info("Process was cancelled. Sending interrupt to R.")
                response.clean()
                robjects.r("stop('Process cancelled by user')")
                raise ProcessError("Process failed.")
        finally:
            session.close()
        # Check for fixed progress markers
        for marker, percentage in progress_markers.items():
            if marker in text:
                update_status_with_check(response, marker, percentage)
                logger.info(marker)
                return

        # 29% to 55%
        if "Interpolating timesteps" in text:
            match = re.search(r"Interpolating timesteps (\d+) - (\d+) / (\d+)", text)
            if match:
                start, end, total = map(int, match.groups())
                progress = end / int(total)
                percentage = 29 + (progress * 26)  # 26 = (55 - 29)
                message = f"Interpolating timesteps {start}-{end} of {total}"
                update_status_with_check(response, message, int(percentage))
                logger.info(message)
                return

        # 67% to 95%
        if "Applying climatologies to file" in text:
            match = re.search(
                r"Applying climatologies to file .* steps (\d+) : (\d+) / (\d+)",
                text,
            )
            if match:
                start, end, total = map(int, match.groups())
                progress = end / int(total)
                percentage = 67 + (progress * 28)  # 28 = (95 - 67)
                message = (
                    f"Applying climatologies to timesteps {start}-{end} of {total}"
                )
                update_status_with_check(response, message, int(percentage))
                logger.info(message)
                return

    def set_monitor():
        # Set the R console monitoring callback
        callbacks.consolewrite_print = custom_console_write

    def remove_monitor():
        # Restore the original R console callback
        callbacks.consolewrite_print = original_console_write

    return set_monitor, remove_monitor
