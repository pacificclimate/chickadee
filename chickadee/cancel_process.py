import json
from pywps.dblog import store_status
from pywps.response.status import WPS_STATUS


def handle_cancel(environ, start_response):
    if environ["REQUEST_METHOD"].upper() != "POST":
        return _simple_json_response(
            start_response,
            {"error": "Method not allowed, use POST"},
            status="405 Method Not Allowed",
        )

    content_length = int(environ.get("CONTENT_LENGTH") or 0)
    body = environ["wsgi.input"].read(content_length)

    try:
        data = json.loads(body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return _simple_json_response(
            start_response, {"error": "Invalid JSON"}, status="400 Bad Request"
        )

    process_uuid = data.get("uuid")
    if not process_uuid:
        return _simple_json_response(
            start_response,
            {"error": "Missing 'uuid' in request body"},
            status="400 Bad Request",
        )
    try:
        store_status(process_uuid, WPS_STATUS.FAILED, "Process cancelled by user", 100)
    except Exception as e:
        return _simple_json_response(
            start_response,
            {"error": f"Failed to update status: {str(e)}"},
            status="500 Internal Server Error",
        )

    return _simple_json_response(
        start_response,
        {"message": f"Process {process_uuid} cancelled."},
        status="200 OK",
    )


def _simple_json_response(start_response, data, status="200 OK"):
    body_bytes = json.dumps(data).encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body_bytes))),
    ]
    start_response(status, headers)
    return [body_bytes]
