response_registry = {}


def track_response(uuid, response):
    response_registry[uuid] = response


def get_response(uuid):
    return response_registry.get(uuid)


def untrack_response(uuid):
    response_registry.pop(uuid, None)
