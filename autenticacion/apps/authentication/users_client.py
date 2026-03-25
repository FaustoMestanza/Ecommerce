import json
from urllib import error, request

from django.conf import settings


class UsersServiceError(Exception):
    """Error al comunicarse con el microservicio de usuarios."""


def _build_url(path: str) -> str:
    base = settings.USUARIOS_SERVICE_URL.rstrip("/")
    return f"{base}{path}"


def _headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    token = settings.USUARIOS_SERVICE_TOKEN
    if token:
        headers["X-Internal-Service-Token"] = token
    return headers


def _request(method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    req = request.Request(
        url=_build_url(path),
        data=body,
        headers=_headers(),
        method=method,
    )

    try:
        with request.urlopen(req, timeout=10) as response:
            raw = response.read().decode("utf-8") or "{}"
            return response.status, json.loads(raw)
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8") or "{}"
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"detail": raw}
        return exc.code, data
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise UsersServiceError(str(exc)) from exc


def register_user(payload: dict) -> tuple[int, dict]:
    return _request("POST", "/api/users/", payload)


def authenticate_user(username: str, password: str) -> tuple[int, dict]:
    return _request(
        "POST",
        "/api/internal/auth-user/",
        {"username": username, "password": password},
    )


def get_user_by_id(user_id: int) -> tuple[int, dict]:
    return _request("GET", f"/api/internal/users/{user_id}/")
