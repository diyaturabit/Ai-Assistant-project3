import httpx

def handle_exception(e: Exception):
    if isinstance(e, httpx.HTTPStatusError):
        return {
            "error": "HTTP error",
            "status_code": e.response.status_code,
            "details": e.response.text,
        }

    elif isinstance(e, httpx.RequestError):
        return {
            "error": "Request failed",
            "details": str(e),
        }

    else:
        return {
            "error": "Unexpected error",
            "details": str(e),
        }
