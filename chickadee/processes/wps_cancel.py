from pywps import Process, LiteralInput
from pywps.response.status import WPS_STATUS
from pywps.dblog import store_status
from pywps.app.exceptions import ProcessError


class CancelProcess(Process):
    def __init__(self):
        inputs = [LiteralInput("uuid", "Process UUID", data_type="string")]
        # No outputs
        super(CancelProcess, self).__init__(
            self._handler,
            identifier="cancel",
            title="Cancel Process",
            abstract="Cancels a running WPS process given its UUID.",
            inputs=inputs,
            outputs=[],
            store_supported=True,
            status_supported=True,
        )

    def _handler(self, request, response):
        try:
            process_uuid = request.inputs.get("uuid")[0].data
        except Exception as e:
            raise ProcessError("Missing or invalid process UUID") from e

        store_status(process_uuid, WPS_STATUS.FAILED, "Process cancelled by user", 100)
        response._update_status(WPS_STATUS.SUCCEEDED, "Process cancelled by user", 100)
        return response
