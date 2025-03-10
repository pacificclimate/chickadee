import os
from pywps.app.Service import Service
from .processes import processes
import cancel_process


def create_app(cfgfiles=None):
    config_files = [os.path.join(os.path.dirname(__file__), "default.cfg")]
    if cfgfiles:
        config_files.extend(cfgfiles)
    if "PYWPS_CFG" in os.environ:
        config_files.append(os.environ["PYWPS_CFG"])

    wps_service = Service(processes=processes, cfgfiles=config_files)

    def application(environ, start_response):
        path_info = environ.get("PATH_INFO", "")

        if path_info == "/wps/cancel-process":
            return cancel_process.handle_cancel(environ, start_response)
        else:
            return wps_service(environ, start_response)

    return application


application = create_app()
