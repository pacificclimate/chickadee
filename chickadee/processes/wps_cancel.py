import os
import signal
from pywps import Process, LiteralInput
from pywps.response.status import WPS_STATUS
from pywps.dblog import store_status, get_session, ProcessInstance
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
            target_uuid = request.inputs.get("uuid")[0].data
        except Exception as e:
            raise ProcessError("Missing or invalid process UUID") from e

        session = get_session()
        process_entry = (
            session.query(ProcessInstance).filter_by(uuid=target_uuid).first()
        )

        if not process_entry:
            session.close()
            raise ProcessError(f"Process {target_uuid} not found.")

        pid = process_entry.pid
        session.close()

        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                store_status(
                    target_uuid, WPS_STATUS.FAILED, "Process cancelled by user", 100
                )
                response.update_status(
                    f"Successfully terminated process {target_uuid} (PID: {pid})", 100
                )
            except ProcessLookupError:
                raise ProcessError(f"Process {target_uuid} (PID: {pid}) not running.")
        else:
            # If no PID is found, just update the status
            store_status(
                target_uuid, WPS_STATUS.FAILED, "Process marked as cancelled", 100
            )
            response.update_status(
                WPS_STATUS.SUCCEEDED,
                f"Marked process {target_uuid} as cancelled (no PID found)",
                100,
            )

        return response
