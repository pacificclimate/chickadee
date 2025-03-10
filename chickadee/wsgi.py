import os
import logging
from pywps.app.Service import Service
from .processes import processes
from .cancel_process import handle_cancel

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def create_app(cfgfiles=None):
    config_files = [os.path.join(os.path.dirname(__file__), "default.cfg")]
    if cfgfiles:
        config_files.extend(cfgfiles)
    if "PYWPS_CFG" in os.environ:
        config_files.append(os.environ["PYWPS_CFG"])

    try:
        wps_service = Service(processes=processes, cfgfiles=config_files)
    except Exception as e:
        logger.error(f"Service initialization failed: {str(e)}")
        raise

    def application(environ, start_response):
        try:
            path_info = environ.get("PATH_INFO", "")
            logger.debug(f"Request to path: {path_info}")

            if path_info == "/wps/cancel-process":
                return handle_cancel(environ, start_response)
            return wps_service(environ, start_response)

        except Exception as e:
            logger.error(f"Request failed: {str(e)}", exc_info=True)
            start_response(
                "500 Internal Server Error", [("Content-type", "text/plain")]
            )
            return [b"Internal server error"]

    return application


application = create_app()
