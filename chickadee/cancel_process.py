import json
import os
import signal
import psutil
from pywps.dblog import store_status, get_session, ProcessInstance
from pywps.response.status import WPS_STATUS


def handle_cancel(environ, start_response):
    if environ["REQUEST_METHOD"].upper() != "POST":
        return _simple_json_response(
            start_response,
            {"error": "Method not allowed, use POST"},
            "405 Method Not Allowed",
        )

    content_length = int(environ.get("CONTENT_LENGTH") or 0)
    body = environ["wsgi.input"].read(content_length)

    try:
        data = json.loads(body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return _simple_json_response(
            start_response, {"error": "Invalid JSON"}, "400 Bad Request"
        )

    process_uuid = data.get("uuid")
    if not process_uuid:
        return _simple_json_response(
            start_response,
            {"error": "Missing 'uuid' in request body"},
            "400 Bad Request",
        )

    session = get_session()
    try:
        process = session.query(ProcessInstance).filter_by(uuid=process_uuid).first()
        if process and process.pid:
            pid = process.pid
            try:
                if process.status in [WPS_STATUS.STARTED, WPS_STATUS.PAUSED]:
                    os.kill(pid, signal.SIGINT)  # Graceful termination

                store_status(
                    process_uuid, WPS_STATUS.FAILED, "Process cancelled by user", 100
                )
                return _simple_json_response(
                    start_response,
                    {"message": f"Process {process_uuid} (PID {pid}) cancelled."},
                    "200 OK",
                )
            except ProcessLookupError:
                return _simple_json_response(
                    start_response,
                    {"error": f"Process {pid} not found."},
                    "404 Not Found",
                )
            except PermissionError:
                return _simple_json_response(
                    start_response,
                    {"error": f"Permission denied to stop process {pid}."},
                    "403 Forbidden",
                )
        else:
            return _simple_json_response(
                start_response,
                {"error": "Process UUID not found or no PID recorded."},
                "404 Not Found",
            )
    except Exception as e:
        return _simple_json_response(
            start_response,
            {"error": f"Failed to update status: {str(e)}"},
            "500 Internal Server Error",
        )
    finally:
        session.close()


def _simple_json_response(start_response, data, status="200 OK"):
    body_bytes = json.dumps(data).encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body_bytes))),
    ]
    start_response(status, headers)
    return [body_bytes]
