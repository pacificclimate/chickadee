import json
from pywps.dblog import store_status, get_session, ProcessInstance
from pywps.response.status import WPS_STATUS


def handle_cancel(environ, start_response):
    def error(msg, code):
        return _simple_json_response(start_response, {"error": msg}, code)

    if environ["REQUEST_METHOD"].upper() != "POST":
        return error("Method not allowed, use POST", "405 Method Not Allowed")

    content_length = int(environ.get("CONTENT_LENGTH") or 0)
    try:
        body = environ["wsgi.input"].read(content_length)
        data = json.loads(body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return error("Invalid JSON", "400 Bad Request")

    process_uuid = data.get("uuid")
    if not process_uuid:
        return error("Missing 'uuid' in request body", "400 Bad Request")

    session = get_session()
    try:
        process = session.query(ProcessInstance).filter_by(uuid=process_uuid).first()
        if not process or not process.pid:
            return error("Process UUID not found or no PID recorded.", "404 Not Found")

        pid = process.pid
        store_status(process_uuid, WPS_STATUS.FAILED, "Process cancelled by user", 100)
        return _simple_json_response(
            start_response,
            {"message": f"Process {process_uuid} (PID {pid}) cancelled."},
            "200 OK",
        )

    except Exception as e:
        return error(f"Failed to update status: {str(e)}", "500 Internal Server Error")
    finally:
        session.close()


def _simple_json_response(start_response, data, status="200 OK"):
    body = json.dumps(data).encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]
    start_response(status, headers)
    return [body]
