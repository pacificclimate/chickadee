### Cancelling a Running WPS Process

The `handle_cancel` function provides an HTTP endpoint for **gracefully cancelling a running WPS process** by sending it a `SIGINT` and updating its status in the PyWPS database.

#### Endpoint

```
POST /wps/cancel-process
```

This endpoint is handled by the `handle_cancel` function via WSGI middleware. It is only accessible using the POST method.

#### Request Format

**Headers**:  
 `Content-Type: application/json`

**Body**:

```json
{ "uuid": "your-process-uuid" }
```

- `uuid` is required and must refer to a running WPS process with a recorded PID in the PyWPS database.

#### Successful Response

```json
{ "message": "Process your-process-uuid (PID 12345) cancelled." }
```

HTTP Status: `200 OK`

#### Error Responses

| Status Code                 | Reason                                                 |
| --------------------------- | ------------------------------------------------------ |
| `400 Bad Request`           | Missing or invalid JSON, or UUID not provided          |
| `403 Forbidden`             | Permission denied when trying to send signal           |
| `404 Not Found`             | No process found for the given UUID or no PID recorded |
| `405 Method Not Allowed`    | Request method was not POST                            |
| `500 Internal Server Error` | Internal database or signal error                      |

---

#### Internals

- Uses `pywps.dblog.get_session()` to query the process from the database.
- Sends `SIGINT` (graceful stop) to the stored PID using `os.kill()`.
- Updates process status using `store_status()` to reflect cancellation as `WPS_STATUS.FAILED`.
- Cleans up the temporary directories using [response.clean()](https://github.com/geopython/pywps/blob/10dd07a9ee55c3033e240fa882eebadfc3ac4ad8/pywps/app/Process.py#L333).
- Closes the database session.

---

#### Example `curl` Request

```bash
curl -X POST http://localhost:5000/wps/cancel-process \
  -H "Content-Type: application/json" \
  -d '{"uuid": "abcd-1234-efgh-5678"}'
```
